import json
import requests
from dataclasses import dataclass, field

def jprint(obj):
	text = json.dumps(obj, sort_keys=True, indent=4)
	print(text)

@dataclass(order=True)
class Card:
	sort_index: int = field(init=False, repr=False)
	name: str
	cn: int
	set: str
	foil: str = "No"
	fullinfo: dict = field(default_factory=dict)
	
	def __post_init__(self):
		object.__setattr__(self, "sort_index", self.name)
		
	def __str__(self):
		return f'{self.name} ({self.cn}, {self.set}) {"[F]" if self.foil == "Yes" else ("[FE]" if self.foil == "Etched" else "")}'


def getCardInfo(card):
	return requests.get(f'https://api.scryfall.com/cards/search?q=cn:{card.cn}%20set:{card.set}%20game:paper')

def getPrice(card):
	response = getCardInfo(card)
	price = None
	# price = response.json()["data"][0]["prices"]["usd" + ("_foil" if card.foil == "Yes" else ("_etched" if card.foil == "Etched" else ""))]
	add = ""
	if (card.foil == "Yes"):
		add = "_foil"
	elif (card.foil == "Etched"):
		add = "_etched"
		
	try:
		prices = response.json()["data"][0]["prices"]
		price = prices["usd" + add]
	except:
		#print(card)
		#print(response)
		exit(f"Something went wrong with card {card.name} ({card.cn} {card.set}). Check the name or the set name")
	
	"""if (price == None or card.foil == "Etched"):
		price = response.json()["data"][0]["prices"]["usd_etched"]"""
		
	if (price == None):
		print(card)
		print(response.json()["data"][0]["prices"])
		exit("Recieved price is type None")
	return float(price)
	
def compareLists(list1, list2):
	if (len(list1) != len(list2)):
		return False
	
	for index in range(len(list1)):
		if (list1[index] != list2[index]):
			return False
	
	return True
	
def getDifferences(list1, list2):
	addLen = max(len(list1), len(list2)) - min(len(list1), len(list2))
	diff = []
	for i in range(min(len(list1), len(list2))):
		diff.append(list1[i] == list2[i])
	for i in range(addLen):
		diff.append(None)
	
	return diff

def allTrue(l):
	for b in l:
		if not b:
			return False
	return True


if (__name__ == "__main__"):
	chip = Card("The Reality Chip", 74,  "NEO")
	chip.fullinfo = getCardInfo(chip).json()
	jprint(chip.fullinfo)
	