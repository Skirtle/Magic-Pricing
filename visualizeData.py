import time, pyodbc, datetime
import getCards as gc, numpy as np, matplotlib.pyplot as plt, random as rand
from openpyxl import Workbook, load_workbook

excelFilename = "MagicPrices.xlsx"

# Open excel workbook
workbook = None
try:
	workbook = load_workbook(filename = excelFilename)
except:
	workbook = Workbook()
	workbook.save(filename = excelFilename)
sheet = workbook.active

def getPriceOfCard(card):
	# Find card in sheet
	row = 2
	while (sheet[f"A{row}"].value != None):
		excelCardInfo = [sheet[f"A{row}"].value, str(sheet[f"B{row}"].value), sheet[f"C{row}"].value, sheet[f"D{row}"].value]
		compared = gc.getDifferences(excelCardInfo, [card.name, card.cn, card.foil, card.set])
		if (gc.allTrue(compared)): break
		row += 1
	else:
		print(card)
		return None
		
		
	# Find date columns
	startColumn = 'E'
	colAsNum = ord(startColumn)
	while (sheet[f"{chr(colAsNum)}1"].value != None):
		colAsNum += 1
	endColumn = chr(colAsNum - 1)

	# Get prices
	dates = np.zeros(len(range(ord(startColumn), ord(endColumn) + 1)), dtype = "datetime64[s]") # X
	prices = np.zeros(len(range(ord(startColumn), ord(endColumn) + 1))) # Y
	for index in range(0, len(dates)):
		fixedColumn = chr(index + ord(startColumn))
		excelDate = sheet[f"{fixedColumn}1"].value
		fixedDate = np.datetime64(excelDate)
		dates[index] = fixedDate
		if (sheet[f"{fixedColumn}{row}"].value == "-"): prices[index] = 0
		else: prices[index] = sheet[f"{fixedColumn}{row}"].value
	
	return (dates, prices)

# List with all cards and price histories for those cards
cards =[]
row = 2
while (sheet[f"A{row}"].value != None):
	# Name, collector number, foiling type, set code
	newCard = gc.Card(sheet[f"A{row}"].value, sheet[f"B{row}"].value, sheet[f"D{row}"].value, sheet[f"C{row}"].value)
	cards.append([newCard, getPriceOfCard(newCard)])
	
	row += 1

# Selected card
card = rand.choice(cards)[0]
dates, prices = getPriceOfCard(card)

plt.style.use('dark_background')
fig, ax = plt.subplots()
ax.plot(dates, prices, **{'color': 'green', 'marker': 'o'})
plt.xlabel("Date")
plt.ylabel("Price")
plt.title(f"{card} price history")
ax.set_ylim(ymin = 0, ymax = 1.2 * max(prices))

ax.yaxis.set_major_formatter('${x:1.2f}')
fig.autofmt_xdate()

plt.show()