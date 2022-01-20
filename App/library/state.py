# Holds the state of the program, such as the items stored in the inventory
# The State class will only store data, and will not itself perform operations on data 
class State:
    def __init__(self, targetTier):
        # Information about the world
        self.itemDependencyGraph = {}         # key: name of an item, value: a list of sub-items that consitute the item
        self.reverseItemDependencyGraph = {}  # key: name of an item, value: a list of super-items that can be formed from the item 
        self.itemToConstituents = {}          # key: name of an item, value: a list of tuples (sub-item, instances) representing the item recipe

        self.itemToTier = {}                  # key: name of an item, value: an integer representing the tier of the item
        self.tierToItem = {}                  # key: an integer representing a tier, value: a list of item names in that tier 
        self.tierToItem[targetTier] = []

        # Information about the inventory
        self.itemNameToNumberOwned = {}       # key: name of an item, value: an integer, representing the number of instances in the inventory

        # Information about goals
        self.itemDesireSatisfaction = {}      # key: name of an item, value: a list [fulfillment, desires], representing the level of satisfaction of each item
