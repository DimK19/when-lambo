import binascii
import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4
from functools import reduce
from copy import deepcopy

class Wallet:
	"""
	"""
	def __init__(self):
		## https://pycryptodome.readthedocs.io/en/latest/src/public_key/rsa.html
		key = RSA.generate(1024)
		self.private_key = key.export_key().decode('ISO-8859-1')
		self.public_key = key.public_key().export_key().decode('ISO-8859-1')
		self.utxos = []
		self.completed_transactions = []

	def as_dict(self):
		## https://peps.python.org/pep-0584/#dict-d1-d2
		return dict(deepcopy(self.__dict__), **{'balance': self.balance()})

	## https://stackoverflow.com/a/141777 TO OVERLOAD CONSTRUCTOR

	def __str__(self):
		"""
		Wallet information and all transactions
		"""
		return f'PRIVATE KEY: {self.private_key}\nPUBLIC_KEY: {self.public_key}\nTRANSACTIONS: {self.completed_transactions}\nUTXOS: {self.utxos}\n'

	def balance(self) -> float:
		try:
			return reduce(lambda accumulator, x: accumulator + x['amount'], self.utxos, 0)
		except Exception:
			return 0

	def get_public_key(self):
		return self.public_key
