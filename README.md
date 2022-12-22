# Magic-Pricing
Record of my collection of cards (ever updating, never settled)

# How to use
* Have Python 3 installed (and some modules I will put here later)
* Have an access database named Magic.accdb
* Edit updatePrices.py such that line 16 says "cnxn = pyodbc.connect(r'Driver={Microsoft Access Driver (\*.mdb, \*.accdb)};DBQ=C:\YOUR-PATH-HERE' + accessFilename + ";")"


# Update 1.1

## Done
* Added visualizer for price history
* Fixed bug with Village Rites (JP) (I had a newline character in there somewhere)

## To do
* Create a UI to select from all cards from the excel sheet
* Add more cards to database
* Likely to remove all old cards from database to make price history of all cards line up better
* Fix cnxn in updatePrices.py to be a dynamic path instead of not
