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


	def __str__(self):
		"""
		Wallet information and all transactions
		"""
		return f'PRIVATE KEY: {self.private_key}\nPUBLIC_KEY: {self.public_key}\nTRANSACTIONS{self.completed_transactions}\n'

	def balance(self) -> float:
		return sum([u["amount"] for u in self.utxos[self.public_key]])

	def get_public_key(self):
		return self.public_key