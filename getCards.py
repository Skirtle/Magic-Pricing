import json
import requests
from dataclasses import dataclass, field

def convTime(t):
	if (t >= 3600):
		unit = "hours"
		t /= 3600
		t = round(t, 2)
	elif (t >= 60):
		unit = "minutes"
		t /= 60
		t = round(t, 2)
	else:
		unit = "seconds"
		t = round(t, 0)
	split = str(t).split(".")
	if (len(split) == 1): dec = "00"
	else: dec = split[1].ljust(2, '0')
	return [split[0] + "." + dec, unit]

def jprint(obj, ind = 2):
	print(json.dumps(obj, sort_keys=True, indent=ind))

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
		
	if (price == None):
		print(card)
		print(response.json()["data"][0]["prices"])
		exit("Recieved price is type None")
	return float(price)
	
def compareLists(list1, list2):
	if (len(list1) != len(list2)):
		return False
	
	for index in range(len(list1)):
		if (str(list1[index]) != str(list2[index])):
			return False
	
	return True
	
def getDifferences(list1, list2):
	addLen = max(len(list1), len(list2)) - min(len(list1), len(list2))
	diff = []
	for i in range(min(len(list1), len(list2))):
		diff.append(str(list1[i]) == str(list2[i]))
	for i in range(addLen):
		diff.append(None)
	
	return diff

def allTrue(l):
	for b in l:
		if not b:
			return False
	return True


if (__name__ == "__main__"):
	t1 = 5
	t2 = 6.1
	t3 = 5.12
	print(convTime(t1)[0])
	print(convTime(t2)[0])
	print(convTime(t3)[0])
	