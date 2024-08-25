# Magic-Pricing
Record of my collection of cards (ever updating, never settled)

# How to use
* Have Python 3 installed (and some modules I will put here later)
* Have an Access database named Magic.accdb (included)
1. Input all cards and relevant information into Magic.accdb
2. Run updatePrices.py
	This will create/update MagicPrices.xlsx
3. (Optional) run visualizeData.py to see price histories of selected cards without the need of an Excel graph
* It should be noted that Scryfall updates their prices once every 24 hours and asks that all requests to the API be, on average, between 50 and 100 ms between one another
* More information can be found at https://scryfall.com/docs/api


# Update 1.1
* Added a visualizer for price history (integrated in the UI)
* Dynamic cnxn rather than hardcoded
* Created a UI to select from all cards from the excel sheet
