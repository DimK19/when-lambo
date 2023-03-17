import time
import json
import configparser
from copy import deepcopy

from Crypto.Hash import SHA256

from blockchain import Blockchain
from transaction import Transaction

## https://docs.python.org/3/library/configparser.html
config = configparser.ConfigParser()
config.read('constants.ini')

class Block:
	## default args for initialization in controller
	def __init__(self, previous_hash = 1, genesis: bool = False, timestamp = None, nonce = 0, list_of_transactions = []):
		self.genesis = genesis
		if(timestamp is None): self.timestamp = time.time()
		self.previous_hash = previous_hash
		self.nonce = nonce
		self.list_of_transactions = deepcopy(list_of_transactions)
		self.capacity = int(config['EXPERIMENTS']['BLOCK_CAPACITY'])

	def __len__(self):
		return len(self.list_of_transactions)

	def __str__(self):
		return f'BLOCK HASH: {self.hash}\nPREVIOUS HASH: {self.previous_hash}\nTRANSACTIONS: {self.list_of_transactions}\n'

	## calculate block hash
	## do not assign to self.hash immediately, helps with validation
	def __hash__(self):
		## https://stackoverflow.com/q/3768895
		## https://stackoverflow.com/a/64469761
		transaction_hashes = [t.transaction_hash for t in self.list_of_transactions]
		td = {
			'timestamp': self.timestamp,
			'nonce': self.nonce,
			'previous_hash': self.previous_hash,
			'all_transaction_hashes': transaction_hashes
		}
		self.hash = SHA256.new(json.dumps(td).encode()).hexdigest()
		return SHA256.new(json.dumps(td).encode()).hexdigest()

	def as_dict(self):
		transactions = [t.as_dict() for t in self.list_of_transactions]
		res = {
			'genesis': self.genesis,
			'timestamp': self.timestamp,
			'nonce': self.nonce,
			'previous_hash': self.previous_hash,
			'list_of_transactions': transactions,
			'hash': self.hash
		}

	def add_transaction(self, t: Transaction):
		self.list_of_transactions.append(t)
