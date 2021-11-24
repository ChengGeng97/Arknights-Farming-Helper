import os     # to read the goals in the goals folder
import queue  # to find toposort
import re     # for parsing the files


"""
0. Read files, arguments
"""

databaseFile = open("database.txt", "r")
inventoryFile = open("inventory.txt", "r")
tier3MatsFile = open("tier3mats.txt", "r")

databaseLines = databaseFile.read().split('\n')
inventoryLines = inventoryFile.read().split('\n')
tier3MatsLines = tier3MatsFile.read().split('\n') 

targetTier = 3

goalPath = os.getcwd() + '\goals'
goalDirectory = os.scandir(goalPath)


# Information about the world
itemDependencyGraph = {}         # key: name of an item, value: a list of sub-items that consitute the item
reverseItemDependencyGraph = {}  # key: name of an item, value: a list of super-items that can be formed from the item 
itemToConstituents = {}          # key: name of an item, value: a list of tuples (sub-item, instances) representing the item recipe

itemToTier = {}                  # key: name of an item, value: an integer representing the tier of the item
tierToItem = {}                  # key: an integer representing a tier, value: a list of item names in that tier 
tierToItem[targetTier] = []

# Information about the inventory
itemNameToNumberOwned = {}       # key: name of an item, value: an integer, representing the number of instances in the inventory

# Information about goals
itemDesireSatisfaction = {}      # key: name of an item, value: a list [fulfillment, desires], representing the level of satisfaction of each item


# Helper functions
def initItem(itemName):
    if itemName not in itemDependencyGraph:
        # Init in Database
        itemDependencyGraph[itemName] = []
        reverseItemDependencyGraph[itemName] = []
        itemToConstituents[itemName] = []
        itemToTier[itemName] = 0

        # Init in inventory
        itemNameToNumberOwned[itemName] = 0

        # Init in desires
        itemDesireSatisfaction[itemName] = [0, 0]

"""
1. Generate a graph where each item points to its constituents.
    Also maintain a table where each item is mapped to the number of each constituent. 
"""

# init regex
instanceLinePattern = '\d+x\s.*'
instanceLineMatcher = re.compile(instanceLinePattern)

xNumberPattern = '\d+x\s'
# Everything beyond the match is name of the item
# We can find the number of instances by dropping the last two characters (known to be x and \s)
xNumberMatcher = re.compile(xNumberPattern)

currentItem = ""

for databaseLine in databaseLines:
    strippedLine = databaseLine.strip()
    
    # Ignore empty lines
    if len(strippedLine) == 0:
        continue

    # This is a number followed by an item
    if instanceLineMatcher.fullmatch(strippedLine):
        (start, end) = xNumberMatcher.search(strippedLine).span()
        instances = int(strippedLine[0 : end - 2])
        subItemName = strippedLine[end : len(strippedLine)]

        initItem(subItemName)
        
        itemDependencyGraph[currentItem].append(subItemName)
        reverseItemDependencyGraph[subItemName].append(currentItem)
        itemToConstituents[currentItem].append((subItemName, instances))
        continue

    # Or else: this is the name of an item
    currentItem = strippedLine
    initItem(currentItem)

"""
2. Establish which materials are Tier-3 (the target tier) 
    Find the mapping from each item to its tier.
    The tier of each item is the max depth of the subtree rooted at the item.
"""

def searchMatTier(materialName, tierNumber, matsDiscovered, minTier, maxTier):
    if materialName in matsDiscovered:
        return (minTier, maxTier)

    matsDiscovered.add(materialName)
    itemToTier[materialName] = tierNumber

    minTier = min(tierNumber, minTier)
    maxTier = max(tierNumber, maxTier)

    for subItem in itemDependencyGraph[materialName]:
        (minTier, maxTier) = searchMatTier(subItem, tierNumber - 1, matsDiscovered, minTier, maxTier)

    for superItem in reverseItemDependencyGraph[materialName]:
        (minTier, maxTier) = searchMatTier(superItem, tierNumber + 1, matsDiscovered, minTier, maxTier)

    return (minTier, maxTier)


for tier3MatsLine in tier3MatsLines:
    strippedLine = tier3MatsLine.strip()

    # Ignore empty lines
    if len(strippedLine) == 0:
        continue

    tier3MatName = strippedLine

    # The entire line is a Tier-3 Mat
    itemToTier[tier3MatName] = targetTier
    tierToItem[targetTier].append(tier3MatName)


for tier3MatName in tierToItem[targetTier]:
    (minTier, maxTier) = searchMatTier(tier3MatName, targetTier, set(), 99, 0)



"""
3. Using the mapping generated in 2, find the mapping from each tier to a list of items within that tier.
"""

for x in range(minTier, maxTier + 1):
    tierToItem[x] = []

for itemName in itemToTier.keys():
    tier = itemToTier[itemName]
    tierToItem[tier].append(itemName)


"""
4. Map the name of each item to its number of instances in the inventory.
"""

for inventoryLine in inventoryLines:
    strippedLine = inventoryLine.strip()

    # This is a number followed by an item
    if instanceLineMatcher.fullmatch(strippedLine):
        (start, end) = xNumberMatcher.search(strippedLine).span()
        instances = int(strippedLine[0 : end - 2])
        itemName = strippedLine[end : len(strippedLine)]

        itemNameToNumberOwned[itemName] = instances


"""
5. Read the Goals. Find the mapping from each item to its desired amount, x.
    Save this mapping as itemName -> [0, x]. The zero is a stand-in for the number of instances satisfied.
"""

for goalFile in goalDirectory:
    if not goalFile.is_file():
        continue

    goalFileContents = open(goalPath + "\\" + goalFile.name, "r")
    goalFileLines = goalFileContents.read().split('\n')

    for goalFileLine in goalFileLines:
        strippedLine = goalFileLine.strip()

        if not instanceLineMatcher.fullmatch(strippedLine):
            continue

        (start, end) = xNumberMatcher.search(strippedLine).span()
        instances = int(strippedLine[0 : end - 2])
        itemName = strippedLine[end : len(strippedLine)]

        itemDesireSatisfaction[itemName][1] = itemDesireSatisfaction[itemName][1] + instances


"""
6. For each tier higher than the target tier:
     - For each item, update the number satisfied by the number owned in the inventory.
     - Find the target-tier value of the item. Update the target-tier satisfaction of its constituents (update both the have and desired columns).
"""

def multiplyRecipe(factor, targetTierValue):
    newTargetTierValue = {}
    
    for item in targetTierValue.keys():
        newTargetTierValue[item] = factor * targetTierValue[item]

    return newTargetTierValue

def findTargetTierValue(item):
    if itemToTier[item] == targetTier:
        return { item: 1 }

    targetTierValue = {}

    for (subItem, instances) in itemToConstituents[item]:
        pain = multiplyRecipe(instances, findTargetTierValue(subItem))

        for key in pain.keys():
            targetTierValue[key] = pain[key]

    return targetTierValue


for higherTier in range(targetTier + 1, maxTier + 1):
    for higherTierItem in tierToItem[higherTier]:
        itemDesireSatisfaction[higherTierItem][0] = itemDesireSatisfaction[higherTierItem][0] + itemNameToNumberOwned[higherTierItem]

        targetTierValue = findTargetTierValue(higherTierItem)

        ownedEquivalent = multiplyRecipe(itemDesireSatisfaction[higherTierItem][0], targetTierValue)
        for targetTierItem in ownedEquivalent.keys():
            itemDesireSatisfaction[targetTierItem][0] = itemDesireSatisfaction[targetTierItem][0] + ownedEquivalent[targetTierItem]

        desiredEquivalent = multiplyRecipe(itemDesireSatisfaction[higherTierItem][1], targetTierValue)
        for targetTierItem in desiredEquivalent.keys():
            itemDesireSatisfaction[targetTierItem][1] = itemDesireSatisfaction[targetTierItem][1] + desiredEquivalent[targetTierItem]

"""
7. For each tier lesser than the target tier:
     - Starting from the lowest tier, convert each item upwards. Count this towards the number of owned instances of the higher item.
"""
for lowerTier in range(1, targetTier):
    for lowerTierItem in tierToItem[lowerTier]:
        superItems = reverseItemDependencyGraph[lowerTierItem]

        if len(superItems) != 1:
            continue

        superItem = superItems[0]

        subItemsOfSuperItems = itemToConstituents[superItem]

        if len(subItemsOfSuperItems) != 1:
            continue

        (subItem, constituents) = subItemsOfSuperItems[0]

        if subItem != lowerTierItem:
            continue

        itemDesireSatisfaction[superItem][0] = itemDesireSatisfaction[superItem][0] + int(itemNameToNumberOwned[lowerTierItem] / constituents)

"""
8. For the target tier:
     - Add the number of computed owned instances to the number of owned instances in the targetTierSatisfaction
     - Then print out itemName (computed owned instances / computed desired instances) 
"""

for targetTierItem in tierToItem[targetTier]:
    itemDesireSatisfaction[targetTierItem][0] = itemDesireSatisfaction[targetTierItem][0] + itemNameToNumberOwned[targetTierItem]

    amountFulfilled = itemDesireSatisfaction[targetTierItem][0]
    amountDesired = itemDesireSatisfaction[targetTierItem][1]

    amountUnsatisfied = max(amountDesired - amountFulfilled, 0)

    print(f'{targetTierItem} ( {amountFulfilled} / {amountDesired} ), {amountUnsatisfied} more needed')
