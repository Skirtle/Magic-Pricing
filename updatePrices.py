import time, pyodbc, sys
import getCards as gc, numpy as np, datetime as dt
from openpyxl import Workbook, load_workbook
from os import getcwd

# Final variables
accessFilename = "Magic.accdb"
excelFilename = "MagicPrices.xlsx"
now = dt.datetime.now()
timeWait = 0.1
dir = getcwd() + "\\"
encoding = "latin-1"
# -name/n for filename, -stop/s for early stop, -close/c for auto close
args = sys.argv
if ("-name" in args or "-n" in args):
	try: nameInd = args.index("-name")
	except ValueError: nameInd = args.index("-n")

	try: excelFilename = args[nameInd + 1]
	except IndexError: exit("InputError: Missing name after " + args[nameInd])

	if (".xlsx" not in excelFilename): excelFilename += ".xlsx"

if ("-stop" in args or "-s" in args):
	try: stopInd = args.index("-stop")
	except ValueError: stopInd = args.index("-s")

	try: earlyStop = int(args[stopInd + 1])
	except IndexError: exit("InputError: Missing number after " + args[stopInd])
	except ValueError: exit("NumberError: Input after " + args[stopInd] + " must be a number")

if ("-close" in args or "-c" in args): autoClose = False
else: autoClose = True

# Connection to database
driverStr = r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ='
pathStr = dir
cnxn = pyodbc.connect(driverStr + dir + accessFilename + ";")
cursor = cnxn.cursor()
cnxn.setdecoding(pyodbc.SQL_CHAR, encoding=encoding)
cnxn.setdecoding(pyodbc.SQL_WCHAR, encoding=encoding)
cnxn.setencoding(encoding=encoding)

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
sheet[f"{column}1"] = dt.datetime(now.year, now.month, now.day)
sheet[f"{column}1"].number_format = "mm/dd/yyyy;@"

# Get prices
rowNumber = 0
addedCount = 0
done = 0
avgWaitTimes = [timeWait]
if (not earlyStop): earlyStop = len(cards)
print(f"Excel file set up. Retreiving prices from scryfall ({earlyStop} cards)")
for card in cards:
	if (done >= earlyStop): break
	start = time.time()
	# Percent done
	perc = round((done / earlyStop) * 100, 2)
	eta = np.average(avgWaitTimes) * (earlyStop - done)
	eta, unit = gc.convTime(eta)

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
			line = f"\r\t{perc}% - Updated {card.name} ({card.cn} {card.set}, {card.foil}) for {singlePrice}, eta = {eta} {unit}"
			print(line + " " * len(line), flush = True, end = "")
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
		line = f"\r\t{perc}% - Added {card.name} ({card.cn} {card.set}, {card.foil}) for {singlePrice}, {eta = } {unit}"
		print(line + " " * len(line), flush = True, end = "")
		addedCount += 1
	
	rowNumber += 1
	done += 1
	time.sleep(timeWait)
	end = time.time()
	avgWaitTimes.append(end - start)

print(f"Added {addedCount} new cards")
print("All cards added and updated, closing files")

# Close everything
cursor.close()
cnxn.close()
workbook.save(filename = excelFilename)
print("All files closed and saved. You may exit this program and access the updated files now")
if (autoClose): input()