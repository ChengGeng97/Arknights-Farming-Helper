# Arknights-Farming-Helper
A command line tool you can use to help you decide what to grind for next.

## What does it do
It shows you how many materials you want, and how many materials you would have if everything in your inventory were converted to Tier-3 materials (Orirock Cluster, RMA70-12 etc.). If you have enough of a lower-tiered material, it converts it upwards, and for any higher-tiered materials, they get converted to their cost at Tier 3.

It can be edited to extend the functionality to keep track of your Chips. Just add the information into `database.txt` and `tier3mats.txt`. 

## How to use it
1. Edit the `inventory.txt` file to track your current Inventory.
2. For any operator you are planning to raise, write down the (Tier-3 and above) materials you would need to raise them into a text file and store it in the `goals` folder. Make sure you follow the format of the example file included. Honestly you could have one big `.txt` where you track everyone's materials, but you probably shouldn't.
3. Run the program (on some command line tool) with `py runner.py`

## Misc.
This thing is now fixed to work with Stormwatch.

It's still not tested properly, but I've used it a lot myself.
