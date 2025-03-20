import argparse
import MagicModule as mm, numpy as np, matplotlib.pyplot as plt, PySimpleGUI as sg
from openpyxl import load_workbook
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

parser = argparse.ArgumentParser(description="Show a line graph of a chosen card's prices")
parser.add_argument("-n", "--name", help="Name of Excel file", default="MagicPrices", type=str)
args = parser.parse_args()

def getPriceOfCard(card):
    #Goes through the input Excel workbook and finds the card and its prices
    
    # Find card in sheet
	row = 2
	while (sheet[f"A{row}"].value != None):
		card_name = sheet[f"A{row}"].value
		card_number = str(sheet[f"B{row}"].value)
		card_foiling = sheet[f"C{row}"].value
		card_set = sheet[f"D{row}"].value
	
		excelCardInfo = [card_name, card_number, card_foiling, card_set]
		compared = mm.getDifferences(excelCardInfo, [card.name, card.cn, card.foil, card.set])
		if (mm.allTrue(compared)): break
		row += 1
	else:
		print(card)
		return None
		
	# Find date columns
	startColumn = 'E'
	colAsNum = mm.excelColToNum(startColumn)
	while (sheet[f"{mm.excelNumToCol(colAsNum)}1"].value != None):
		colAsNum += 1
	endColumn = mm.excelNumToCol(colAsNum - 1)

	# Get prices
	start_index = mm.excelColToNum(startColumn)
	end_index = mm.excelColToNum(endColumn) + 1
	data_len = end_index - start_index
	dates = np.zeros(data_len, dtype = "datetime64[s]") # X data
	prices = np.zeros(data_len) # Y data
	
	for index in range(len(dates)):
		fixedColumn = mm.excelNumToCol(index + mm.excelColToNum(startColumn))
		dates[index] = np.datetime64(sheet[f"{fixedColumn}1"].value)
		if (sheet[f"{fixedColumn}{row}"].value == "-"): prices[index] = 0 # Price cannot be found for this date, possible if card was added at a later time
		else: prices[index] = sheet[f"{fixedColumn}{row}"].value # Otherwise, get the price
	
	return (dates, prices)

def getAllCards():
	# List with all cards and price histories for those cards
	cards = []
	row = 2
	while (sheet[f"A{row}"].value != None):
		# Name, collector number, foiling type, set code
		card_name = sheet[f"A{row}"].value
		card_number = sheet[f"B{row}"].value
		card_foil = sheet[f"D{row}"].value
		card_set = sheet[f"C{row}"].value
		newCard = mm.Card(card_name, card_number, card_foil, card_set)
		cards.append([newCard, getPriceOfCard(newCard)])
		row += 1
	
	return cards

def returnCardData(item, list):
    for index,value in enumerate(list):
        if (item == list[index][0]):
            return list[index][1][0], list[index][1][1]
    return np.array([]), np.array([])

def draw_figure_w_toolbar(canvas, fig, canvas_toolbar):
    if canvas.children:
        for child in canvas.winfo_children():
            child.destroy()
    if canvas_toolbar.children:
        for child in canvas_toolbar.winfo_children():
            child.destroy()
    figure_canvas_agg = FigureCanvasTkAgg(fig, master=canvas)
    figure_canvas_agg.draw()
    toolbar = Toolbar(figure_canvas_agg, canvas_toolbar)
    toolbar.update()
    figure_canvas_agg.get_tk_widget().pack(side='right', fill='both', expand=1)

class Toolbar(NavigationToolbar2Tk):
    def __init__(self, *args, **kwargs):
        super(Toolbar, self).__init__(*args, **kwargs)

if __name__ == "__main__":
	# Open excel workbook
	excelFilename = args.name
	if (excelFilename == ""):
		excelFilename = "MagicPrices.xlsx"
	elif (".xlsx" not in excelFilename):
		excelFilename = excelFilename + ".xlsx"
	
	try:
		workbook = load_workbook(filename = excelFilename)
	except:
		exit(f"{excelFilename} not found")
	sheet = workbook.active
 
 	# Selected card
	cards = getAllCards()
	cardNames = [card[0] for card in cards]
	cardNames.sort(key = lambda x: x.name) # Default is sort by name. Will add ability to sort by other metrics (cn, set, latest price, foiling)
	
	layout = [
		[sg.Combo(cardNames, readonly=True, key = "_CARD_", enable_events=True), sg.B("Plot"), sg.B('Exit')],
		[sg.Canvas(key='controls_cv')],
		[sg.T('History:')],
		[sg.Column(layout=[[sg.Canvas(key='fig_cv', size=(400 * 2, 400))]], background_color='#DAE0E6', pad=(0, 0))]

	]
	window = sg.Window('Card Price History Viewer', layout)

	selectedCard = None
	while True:
		event, values = window.read()
		# An exit
		if event in (sg.WIN_CLOSED, 'Exit'):
			break

		# Event for selecting a card via dropdown menu
		elif event == "_CARD_":
			selectedCard = values["_CARD_"]
   
		# Event for Plot button
		elif event == 'Plot':
			# Create chart and fix size
			fig, ax = plt.subplots()
			DPI = fig.get_dpi()
			fig.set_size_inches(404 * 2 / float(DPI), 404 / float(DPI))
			
			# Plot data and fix labels
			dates, prices = returnCardData(selectedCard, cards)
			if (dates.size != prices.size or dates.size == 0 or prices.size == 0):
				exit(f"Error with date/price, {dates=}, {prices=}, exitting.")
			ax.plot(dates, prices, **{'color': 'green', 'marker': 'o'})
			plt.xlabel("Date")
			plt.ylabel("Price")
			plt.title(f"{selectedCard} price history")
			prices = prices[~np.isnan(prices)] # Remove NaN from prices
			ax.set_ylim(ymin = 0, ymax = 1.2 * max(prices))
			ax.yaxis.set_major_formatter('${x:1.2f}')
			fig.autofmt_xdate()
   
			# Get min and max values and annotate (https://stackoverflow.com/questions/43374920/how-to-automatically-annotate-maximum-value-in-pyplot)
			dateMin = dates[np.argmin(prices)]
			priceMin = prices.min()
   
			dateMax = dates[np.argmax(prices)]
			priceMax = prices.max()
			
			bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
			arrowprops=dict(arrowstyle="->",connectionstyle="angle,angleA=0,angleB=90")
			kw = dict(xycoords='data', arrowprops=arrowprops, bbox=bbox_props, ha="right", va="top")
			ax.annotate(f"${priceMin}", xy=(dateMin, priceMin), xytext=(0, -30), textcoords="offset points", **kw)
			ax.annotate(f"${priceMax}", xy=(dateMax, priceMax), xytext=(0, -30), textcoords="offset points", **kw)

			# Show data
			draw_figure_w_toolbar(window['fig_cv'].TKCanvas, fig, window['controls_cv'].TKCanvas)

	window.close()