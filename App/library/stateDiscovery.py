# This file contains all the operations necessary to discover the actual state of the program

"""
1. Generate a graph where each item points to its constituents.
    Also maintain a table where each item is mapped to the number of each constituent. 
"""
def initItem(state, itemName):
    if itemName not in state.itemDependencyGraph:
        # Init in Database
        state.itemDependencyGraph[itemName] = []
        state.reverseItemDependencyGraph[itemName] = []
        state.itemToConstituents[itemName] = []
        state.itemToTier[itemName] = 0

        # Init in inventory
        state.itemNameToNumberOwned[itemName] = 0

        # Init in desires
        state.itemDesireSatisfaction[itemName] = [0, 0]

def parseDatabaseLines(state, databaseLines, instanceLineMatcher, xNumberMatcher):
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

            initItem(state, subItemName)
        
            state.itemDependencyGraph[currentItem].append(subItemName)
            state.reverseItemDependencyGraph[subItemName].append(currentItem)
            state.itemToConstituents[currentItem].append((subItemName, instances))
            continue

        # Or else: this is the name of an item
        currentItem = strippedLine
        initItem(state, currentItem)


"""
2. Establish which materials are Tier-3 (the target tier) 
    Find the mapping from each item to its tier.
    The tier of each item is the max depth of the subtree rooted at the item.
"""
def searchMatTier(state, materialName, tierNumber, matsDiscovered, minTier, maxTier):
    if materialName in matsDiscovered:
        return (minTier, maxTier)

    matsDiscovered.add(materialName)
    state.itemToTier[materialName] = tierNumber

    minTier = min(tierNumber, minTier)
    maxTier = max(tierNumber, maxTier)

    for subItem in state.itemDependencyGraph[materialName]:
        (minTier, maxTier) = searchMatTier(state, subItem, tierNumber - 1, matsDiscovered, minTier, maxTier)

    for superItem in state.reverseItemDependencyGraph[materialName]:
        (minTier, maxTier) = searchMatTier(state, superItem, tierNumber + 1, matsDiscovered, minTier, maxTier)

    return (minTier, maxTier)


def findMaterialsOfTargetTier(state, targetTier, tier3MatsLines):
    minTier = 0
    maxTier = 99
    
    for tier3MatsLine in tier3MatsLines:
        strippedLine = tier3MatsLine.strip()

        # Ignore empty lines
        if len(strippedLine) == 0:
            continue

        tier3MatName = strippedLine

        # The entire line is a Tier-3 Mat
        state.itemToTier[tier3MatName] = targetTier
        state.tierToItem[targetTier].append(tier3MatName)

    for tier3MatName in state.tierToItem[targetTier]:
        (foundMinTier, foundMaxTier) = searchMatTier(state, tier3MatName, targetTier, set(), 99, 0)
        minTier = min(foundMinTier, minTier)
        maxTier = max(foundMaxTier, maxTier)

    return (minTier, maxTier)


"""
3. Using the mapping generated in 2, find the mapping from each tier to a list of items within that tier.
"""
def findMaterialsInEachTier(state, minTier, maxTier):
    for x in range(minTier, maxTier + 1):
        state.tierToItem[x] = []

    for itemName in state.itemToTier.keys():
        tier = state.itemToTier[itemName]
        state.tierToItem[tier].append(itemName)


"""
4. Map the name of each item to its number of instances in the inventory.
"""
def findInstancesOfEachItem(state, inventoryLines, instanceLineMatcher, xNumberMatcher):
    for inventoryLine in inventoryLines:
        strippedLine = inventoryLine.strip()

        # This is a number followed by an item
        if instanceLineMatcher.fullmatch(strippedLine):
            (start, end) = xNumberMatcher.search(strippedLine).span()
            instances = int(strippedLine[0 : end - 2])
            itemName = strippedLine[end : len(strippedLine)]

            state.itemNameToNumberOwned[itemName] = instances

"""
5. Read the Goals. Find the mapping from each item to its desired amount, x.
    Save this mapping as itemName -> [0, x]. The zero is a stand-in for the number of instances satisfied.
"""
def readGoals(state, goalDirectory, goalPath, instanceLineMatcher, xNumberMatcher):
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

            state.itemDesireSatisfaction[itemName][1] = state.itemDesireSatisfaction[itemName][1] + instances
