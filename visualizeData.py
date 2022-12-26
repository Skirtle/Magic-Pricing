import MagicModule as mm, numpy as np, matplotlib.pyplot as plt, PySimpleGUI as sg
from openpyxl import Workbook, load_workbook
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


# Open excel workbook
excelFilename = "MagicPrices.xlsx"
workbook = None
try:
	workbook = load_workbook(filename = excelFilename)
except:
	exit(f"{excelFilename} not found")
sheet = workbook.active

def getPriceOfCard(card):
	# Find card in sheet
	row = 2
	while (sheet[f"A{row}"].value != None):
		excelCardInfo = [sheet[f"A{row}"].value, str(sheet[f"B{row}"].value), sheet[f"C{row}"].value, sheet[f"D{row}"].value]
		compared = mm.getDifferences(excelCardInfo, [card.name, card.cn, card.foil, card.set])
		if (mm.allTrue(compared)): break
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
		dates[index] = np.datetime64(sheet[f"{fixedColumn}1"].value)
		if (sheet[f"{fixedColumn}{row}"].value == "-"): prices[index] = 0
		else: prices[index] = sheet[f"{fixedColumn}{row}"].value
	
	return (dates, prices)

def getAllCards():
	# List with all cards and price histories for those cards
	cards =[]
	row = 2
	while (sheet[f"A{row}"].value != None):
		# Name, collector number, foiling type, set code
		newCard = mm.Card(sheet[f"A{row}"].value, sheet[f"B{row}"].value, sheet[f"D{row}"].value, sheet[f"C{row}"].value)
		cards.append([newCard, getPriceOfCard(newCard)])
		
		row += 1
	
	return cards

def returnData(item, list):
    for index,value in enumerate(list):
        if (item == list[index][0]):
            return list[index][1][0], list[index][1][1]
    return None, None

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
	# Selected card
	cards = getAllCards()
	cardNames = [card[0] for card in cards]
	cardNames.sort(key = lambda x: x.name)

	
	layout = [
		[sg.Combo(cardNames, readonly=True, key = "_CARD_", enable_events=True), sg.B("Plot"), sg.B('Exit')],
		# [sg.T('Controls:')],
		[sg.Canvas(key='controls_cv')],
		[sg.T('History:')],
		[sg.Column(
			layout=[
				[sg.Canvas(key='fig_cv',
						# it's important that you set this size
						size=(400 * 2, 400)
						)]
			],
			background_color='#DAE0E6',
			pad=(0, 0)
		)],
		[sg.B('Alive?')]

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
			dates, prices = returnData(selectedCard, cards)
			ax.plot(dates, prices, **{'color': 'green', 'marker': 'o'})
			plt.xlabel("Date")
			plt.ylabel("Price")
			plt.title(f"{selectedCard} price history")
			ax.set_ylim(ymin = 0, ymax = 1.2 * max(prices))
			ax.yaxis.set_major_formatter('${x:1.2f}')
			fig.autofmt_xdate()
			
			# Show data
			draw_figure_w_toolbar(window['fig_cv'].TKCanvas, fig, window['controls_cv'].TKCanvas)

	window.close()