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
	cn: str
	set: str
	foil: str = "No"
	quantity: int = 1
	fullinfo: dict = field(default_factory=dict)
	
	def __post_init__(self):
		object.__setattr__(self, "sort_index", self.name)
		
	def __str__(self):
		return f'{self.name} ({self.cn}, {self.set}) {"[F]" if self.foil == "Yes" else ("[FE]" if self.foil == "Etched" else "")}'

class InvalidCardException(Exception):
    def __init__(self, card):
        self.card = card
        super().__init__(f"Card {card} not found")
        
class InvalidQueryException(Exception):
    def __init__(self, query):
        self.query = query
        super().__init__(f"Bad query {query:}")


def getCardInfo(card):
	req = requests.get(f'https://api.scryfall.com/cards/search?q=cn:\"{card.cn}\"%20set:{card.set}%20game:paper')
	if (req.json()["object"] == "error"):
		req = requests.get(f"https://scryfall.com/search?q=cn%3D{card.cn}+set%3A{card.set}")
	
	return req

def getPrice(card):
	response = getCardInfo(card)
	price = None
	add = ""
	if (card.foil == "Yes" or card.foil == "True"):
		add = "_foil"
	elif (card.foil == "Etched"):
		add = "_etched"
		
	try:
		prices = response.json()["data"][0]["prices"]
		price = prices["usd" + add]
	except:
		#print(card)
		#print(response)
		raise InvalidCardException(card)
		
	if (price == None):
		print(card)
		print(response.json()["data"][0]["prices"])
		print("Recieved price is type None")
		try:
			price = prices["usd"]
		except:
			exit("Total price failure.")
	if (price == None):
		price = 0
		print("Price set to 0")
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

def validate(card):
	info = getCardInfo(card).json()
	try:
		actual = info["data"][0]["name"]
	except KeyError:
		print(f"KeyError: Something went from with {card}")
		return False, "ERROR"
	return actual == card.name, actual

def _decompose(number):
	# This function and numToCol() found on https://codereview.stackexchange.com/questions/182733/base-26-letters-and-base-10-using-recursion
    number -= 1
    if number < 26: yield number
    else:
        number, remainder = divmod(number, 26)
        yield from _decompose(number)
        yield remainder

def numToCol(number):
    return ''.join(chr(ord('A') + part) for part in _decompose(number))

if (__name__ == "__main__"):
	# https://api.scryfall.com/cards/search?q=cn:\"185\"%20set:pm14%20game:paper
	c = Card("Revel in Riches", "1117", "XLN", foil = "Yes")
	print(c)
	print(getPrice(c))