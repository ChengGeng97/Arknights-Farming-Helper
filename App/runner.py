import os     # to read the goals in the goals folder
import re     # for parsing the files

from library.state import State
from library.stateDiscovery import findInstancesOfEachItem, findMaterialsInEachTier, findMaterialsOfTargetTier, parseDatabaseLines, readGoals
from library.algorithm import convertHigherTierItemsToTargetTierValue, convertLowerTierItemsToTargetTierValue, printResults


# Open files
databaseFile = open("database.txt", "r")
inventoryFile = open("inventory.txt", "r")
tier3MatsFile = open("tier3mats.txt", "r")

databaseLines = databaseFile.read().split('\n')
inventoryLines = inventoryFile.read().split('\n')
tier3MatsLines = tier3MatsFile.read().split('\n')

targetTier = 3

goalPath = os.getcwd() + '\goals'
goalDirectory = os.scandir(goalPath)


# Initialize regex
instanceLinePattern = '\d+x\s.*' # Matches one well-formed line in the database, such as "20x Orirock"
instanceLineMatcher = re.compile(instanceLinePattern)

xNumberPattern = '\d+x\s'  # Matches the instances specified in a well-formed line in the database, such as "20x "
# The number of instances is found by dropping the last two characters (known to be x and \s)
xNumberMatcher = re.compile(xNumberPattern)



# Discover state
state = State(targetTier)

parseDatabaseLines(state, databaseLines, instanceLineMatcher, xNumberMatcher)
(minTier, maxTier) = findMaterialsOfTargetTier(state, targetTier, tier3MatsLines)
findMaterialsInEachTier(state, minTier, maxTier)
findInstancesOfEachItem(state, inventoryLines, instanceLineMatcher, xNumberMatcher)
readGoals(state, goalDirectory, goalPath, instanceLineMatcher, xNumberMatcher)

# Find the target tier value of items
convertHigherTierItemsToTargetTierValue(state, targetTier, maxTier)
convertLowerTierItemsToTargetTierValue(state, targetTier)

# Print results
printResults(state, targetTier)
