import time
import json
import configparser

from Crypto.Hash import SHA256

from blockchain import Blockchain
from transaction import Transaction

## https://docs.python.org/3/library/configparser.html
config = configparser.ConfigParser()
config.read('constants.ini')

class Block:
	def __init__(self, chain: Blockchain, genesis: bool = False):
		self.genesis = genesis
		if(chain is None):
			if(genesis):
				self.previous_hash = 1
				self.nonce = 0
				self.index = 0
			else:
				raise Exception("Cannot append to empty blockchain")
		else:
			if(genesis):
				raise Exception("Cannot add genesis block to existing blockchain")
			else:
				self.previous_hash = chain.get_latest_block_hash()
				self.nonce = nonce
				self.index = len(c)

		self.timestamp = time.time()
		self.previous_hash = None
		self.timestamp = time.time()
		self.hash = None
		self.nonce = 0
		self.list_of_transactions = []
		self.capacity = int(config['EXPERIMENTS']['BLOCK_CAPACITY'])

	def __len__(self):
		return len(self.list_of_transactions)

	def __str__(self):
		return f'BLOCK HASH: {self.hash}\nPREVIOUS HASH: {self.previous_hash}\nTRANSACTIONS: {self.list_of_transactions}\n'

	## do not assign to self.hash immediately, helps with validation
	def calculate_block_hash(self):
		## https://stackoverflow.com/q/3768895
		## https://stackoverflow.com/a/64469761
		return SHA256.new(json.dumps(self.__dict__, default = vars).encode('ISO-8859-2')).hexdigest()

	def add_transaction(self, t: Transaction):
		self.list_of_transactions.append(t)
