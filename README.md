# Arknights-Farming-Helper
A command line tool you can use to help you decide what to grind for next.

## What does it do
It shows you how many materials you want, and how many materials you would have if everything in your inventory were converted to Tier-3 materials (Orirock Cluster, RMA70-12 etc.). If you have enough of a lower-tiered material, it converts it upwards, and for any higher-tiered materials, they get converted to their cost at Tier 3.

The app only makes use of Elite Materials. So adding the information about the Chips into `database.txt` isn't going to extend the functionality due to the way the code was written.

## How to use it
1. Edit the `inventory.txt` file to track your current Inventory.
2. For any operator you are planning to raise, write down the (Tier-3 and above) materials you would need to raise them into a text file and store it in the `goals` folder. Make sure you follow the format of the example file included. Honestly you could have one big `.txt` where you track everyone's materials, but you probably shouldn't.
3. Run the program (on some command line tool) with `py yeet.py`

I am too lazy to post a screenshot I need to get back to actual homework.

## Misc.
This thing is going to break once Stormwatch releases for global (assuming that you are on global). Feel free to remind me to fix that whenever Stormwatch releases.

This thing wasn't tested beyond me doing some manual calculations. It was written to convince myself that I would be grinding "correctly" for Under Tides. Don't put too much faith into it.
