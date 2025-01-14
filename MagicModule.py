import json, requests, csv
from dataclasses import dataclass, field
from datetime import datetime
from io import StringIO
from hashlib import sha256
from time import sleep

_cache = None

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

def get_price_from_json(card, response):
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

	return price

def call_api(card):
	req = requests.get(f'https://api.scryfall.com/cards/search?q=cn:\"{card.cn}\"%20set:{card.set}%20game:paper')
	if (req.json()["object"] == "error"):
		req = requests.get(f"https://scryfall.com/search?q=cn%3D{card.cn}+set%3A{card.set}")
	sleep(0.1)
	return req

def getCardInfo(card, use_cache = False):
	global _cache
	failed = False
	
 
	# Try to read from cache
	if (use_cache):
		card_hash = generate_card_hash(card)
		value = next((row for row in _cache if row[0] == card_hash), None)
  
		try:
			price = value[1]
			return price
		except:
			failed = True
	
	if (failed): price = get_price_from_json(card, call_api(card))
	
	# Add to cache
	if (failed and use_cache): addToCache(card, price)
	return price

def getPrice(card, use_cache = False):
	global _cache
	if (_cache == None and use_cache): 
		_cache = load_cache()
  
	price = getCardInfo(card, use_cache)
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

def log(msg, close=False, printMsg=False):
	with open("log.txt", "a") as log:
		now = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
		log.write(f"{now}: {msg}\n")
	if (printMsg): print(msg)
	if (close): exit(msg)

def excelColToNum(column: str):
	num = 0
	mult = len(column) - 1
	for char in column:
		base = ord(char) - 64
		num += base * int(pow(26, mult))
		mult -= 1
	return num

def excelNumToCol(num: int):
	res = ""
	while (num > 0):
		num -= 1
		res = chr((num % 26) + 65) + res
		num = num//26
	return res

def load_cache():
	global _cache
	with open("price.cache", "r") as file:
		cards = []
		while True:
			card = file.readline()
			if not card: break
			card_split = card.strip().split(",")
			cards.append(card_split)
		_cache = cards
		return cards

def addToCache(card: Card, price: float, reset: bool = False):
	global _cache
	same_date = False
	with open("price.cache", "r") as file:
		date = file.readline().strip()
		if (date): 
			current_date = datetime.now()
			current_date = current_date.strftime('%m/%d/%Y')
			same_date = date == current_date
	
	if (not same_date):
		file = open("price.cache", "w")
		file.write(datetime.now().strftime("%m/%d/%Y") + "\n")
		file.close()
	
	with open("price.cache", "a") as file:
		file.write(f"{generate_card_hash(card)},{price}\n")

def generate_card_hash(card: Card):
	return sha256(f"{card.name}{card.cn}{card.foil}{card.set}".encode()).hexdigest()

if (__name__ == "__main__"):
	pass