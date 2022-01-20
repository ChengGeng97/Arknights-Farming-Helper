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

def findTargetTierValue(state, item, targetTier):
    if state.itemToTier[item] == targetTier:
        return { item: 1 }

    targetTierValue = {}

    for (subItem, instances) in state.itemToConstituents[item]:
        pain = multiplyRecipe(instances, findTargetTierValue(state, subItem, targetTier))

        for key in pain.keys():
            targetTierValue[key] = pain[key]

    return targetTierValue

def convertHigherTierItemsToTargetTierValue(state, targetTier, maxTier):
    for higherTier in range(targetTier + 1, maxTier + 1):
        for higherTierItem in state.tierToItem[higherTier]:
            state.itemDesireSatisfaction[higherTierItem][0] = state.itemDesireSatisfaction[higherTierItem][0] + state.itemNameToNumberOwned[higherTierItem]

            targetTierValue = findTargetTierValue(state, higherTierItem, targetTier)

            ownedEquivalent = multiplyRecipe(state.itemDesireSatisfaction[higherTierItem][0], targetTierValue)
            for targetTierItem in ownedEquivalent.keys():
                state.itemDesireSatisfaction[targetTierItem][0] = state.itemDesireSatisfaction[targetTierItem][0] + ownedEquivalent[targetTierItem]

            desiredEquivalent = multiplyRecipe(state.itemDesireSatisfaction[higherTierItem][1], targetTierValue)
            for targetTierItem in desiredEquivalent.keys():
                state.itemDesireSatisfaction[targetTierItem][1] = state.itemDesireSatisfaction[targetTierItem][1] + desiredEquivalent[targetTierItem]


"""
7. For each tier lesser than the target tier:
     - Starting from the lowest tier, convert each item upwards. Count this towards the number of owned instances of the higher item.
"""
def convertLowerTierItemsToTargetTierValue(state, targetTier):
    for lowerTier in range(1, targetTier):
        for lowerTierItem in state.tierToItem[lowerTier]:
            superItems = state.reverseItemDependencyGraph[lowerTierItem]

            if len(superItems) != 1:
                continue

            superItem = superItems[0]

            subItemsOfSuperItems = state.itemToConstituents[superItem]

            if len(subItemsOfSuperItems) != 1:
                continue

            (subItem, constituents) = subItemsOfSuperItems[0]

            if subItem != lowerTierItem:
                continue

            state.itemDesireSatisfaction[superItem][0] = state.itemDesireSatisfaction[superItem][0] + int(state.itemNameToNumberOwned[lowerTierItem] / constituents)


"""
8. For the target tier:
     - Add the number of computed owned instances to the number of owned instances in the targetTierSatisfaction
     - Then print out itemName (computed owned instances / computed desired instances) 
"""
def printResults(state, targetTier):
    for targetTierItem in state.tierToItem[targetTier]:
        state.itemDesireSatisfaction[targetTierItem][0] = state.itemDesireSatisfaction[targetTierItem][0] + state.itemNameToNumberOwned[targetTierItem]

        amountFulfilled = state.itemDesireSatisfaction[targetTierItem][0]
        amountDesired = state.itemDesireSatisfaction[targetTierItem][1]

        amountUnsatisfied = max(amountDesired - amountFulfilled, 0)

        print(f'{targetTierItem} ( {amountFulfilled} / {amountDesired} ), {amountUnsatisfied} more needed')
