import json
import requests
from dataclasses import dataclass, field

def jprint(obj):
	text = json.dumps(obj, sort_keys=True, indent=4)
	print(text)

@dataclass(order=True, frozen=True)
class Card:
	sort_index: int = field(init=False, repr=False)
	name: str
	cn: int
	set: str
	foil: str = "No"
	
	def __post_init__(self):
		object.__setattr__(self, "sort_index", self.name)
		
	def __str__(self):
		return f'{self.name} ({self.cn}, {self.set}) {"[F]" if self.foil == "Yes" else ("[FE]" if self.foil == "Etched" else "")}'


def getPrice(card):
	response = requests.get(f'https://api.scryfall.com/cards/search?q=cn:{card.cn}%20set:{card.set}%20game:paper')
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
		exit(f"Something went wrong with card {card.name} ({card.cn} {card.set}). Check the name or the set name!")
	
	"""if (price == None or card.foil == "Etched"):
		price = response.json()["data"][0]["prices"]["usd_etched"]"""
		
	if (price == None):
		print(card)
		print(response.json()["data"][0]["prices"])
		exit("Recieved price is type None")
	return float(price)


if (__name__ == "__main__"):
	legacyBlueprint = Card("Food man", 5, "C21", "Yes")
	listBlueprint = Card("Urza's Blueprints", 277, "PLIST")

	print(getPrice(legacyBlueprint))
	print(getPrice(listBlueprint))