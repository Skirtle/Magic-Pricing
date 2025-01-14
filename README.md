# How to use

## 0. Pre-requirements
* Python installed (I'm using 3.12.1)
* Have an Access database with the following columns:
  * Name as Short Text
  * CollectorNumber as Short Text
  * Set as Short Text
  * Foil as Short Text
  * Amount as Number
  * Date as Date/Time

## 1. Run "python .\updatePrices.py" with any arguments requested
* Some helpful arguments include:
  * -h, --help: Get help message
  * -n, --name: Output Excel file's name
  * -q, --sql: SQL query when accessing the Access database
  * -c, --close: Closes the terminal when done
  * -p, --print: Print progress of cards as prices are found
  * -v, --validate: Validates that all cards in the database can be found correctly
  * -e, --export: Exports into an Excel file (May not work right now)
  * -E, --export_only: Only export into Excel file (May not work right now)
  * --comment: Adds a comment to the log file when ran
  * --no_cache: Do not cache prices

## 2. View data
* Two ways to check the data
  * Run "python .\visualizeData.py"
  * Open the created Excel file (default is MagicPrices.xlsx)


# Updates and bugs
I update a [Trello Board](https://trello.com/b/tSz5I1D7/mtg) with known bugs and planned features, plus the current progress of those features.

# Contact
* Discord: .skirtle
* Email: daltonkajander@yahoo.com