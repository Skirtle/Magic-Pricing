import time, pyodbc, datetime
import getCards as gc
from openpyxl import Workbook, load_workbook
from os import getcwd

# Final variables
accessFilename = "Magic.accdb"
excelFilename = "MagicPrices.xlsx"
now = datetime.datetime.now()
timeWait = 0.2
dir = getcwd() + "\\"

# Connection to database
driverStr = r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ='
pathStr = dir
cnxn = pyodbc.connect(driverStr + dir + accessFilename + ";")
cursor = cnxn.cursor()
cnxn.setdecoding(pyodbc.SQL_CHAR, encoding='utf-8')
cnxn.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-8')
cnxn.setencoding(encoding='utf-8')

# Open excel workbook
workbook = None
try:
	workbook = load_workbook(filename = excelFilename)
except:
	workbook = Workbook()
	workbook.save(filename = excelFilename)
sheet = workbook.active
sheet["A1"] = "Card"
sheet["B1"] = "CN"
sheet["C1"] = "Foiling"
sheet["D1"] = "Set"

# Get all cards
print("Accessing database for cards")
cursor.execute("select * from Cards")
rows = cursor.fetchall()
cards = [gc.Card(c[0], c[1], c[2], c[3]) for c in rows]
print("Cards collected. Setting up excel file for new entries")

# Get new column for prices
column = 1
while (sheet[f"{chr(ord('@') + column)}1"].value != None):
	column += 1
column = chr(ord('@') + column)
sheet[f"{column}1"] = datetime.datetime(now.year, now.month, now.day)
sheet[f"{column}1"].number_format = "mm/dd/yyyy;@"

# Get prices
print("Excel file set up. Retreiving prices from scryfall")
price = 0
rowNumber = 0
addedCount = 0
for card in cards:
	""" Excel sheet: A - Card, B - Collector Number (CN), C - Foiling, D - Set, E: - Date* """
	singlePrice = gc.getPrice(card)
	
	# Search for an already existing cell with card name, collector number, foiling, and set
	rowNumber = 1
	found = False
	while (sheet[f"A{rowNumber}"].value != None):
		excelCardInfo = [sheet[f"A{rowNumber}"].value, str(sheet[f"B{rowNumber}"].value), sheet[f"C{rowNumber}"].value, sheet[f"D{rowNumber}"].value]
		acessCardInfo = [card.name, str(card.cn), card.foil, card.set]
		compared = gc.getDifferences(excelCardInfo, acessCardInfo)
		if (gc.allTrue(compared)):
			sheet[f"{column}{rowNumber}"] = singlePrice
			sheet[f"{column}{rowNumber}"].number_format = '"$"#,##0.00_);("$"#,##0.00)'
			print(f"\tUpdated {card.name} ({card.cn} {card.set}, {card.foil}) for {singlePrice}")
			found = True
			break
		else:
			rowNumber += 1
	
	# Went through all cards in sheet and card was not found. Add at latest checked rowNumber
	if (not found):
		sheet[f"A{rowNumber}"] = card.name
		sheet[f"B{rowNumber}"] = card.cn
		sheet[f"C{rowNumber}"] = card.foil
		sheet[f"D{rowNumber}"] = card.set
		sheet[f"{column}{rowNumber}"] = singlePrice
		sheet[f"{column}{rowNumber}"].number_format = '"$"#,##0.00_);("$"#,##0.00)'
		print(f"\tAdded {card.name} ({card.cn} {card.set}, {card.foil}) for {singlePrice}")
		addedCount += 1
	rowNumber += 1
	time.sleep(timeWait)
print(f"Added {addedCount} new cards")
print("All cards added and updated, closing files")

# Close everything
cursor.close()
cnxn.close()
workbook.save(filename = excelFilename)
print("All files closed and saved. You may exit this program and access the updated files now")
input()