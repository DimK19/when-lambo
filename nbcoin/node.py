from copy import deepcopy
import configparser
import requests
from time import perf_counter, sleep
import json
import base64

from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5, pkcs1_15

from block import Block
from wallet import Wallet
from transaction import Transaction
from blockchain import Blockchain

config = configparser.ConfigParser()
config.read('constants.ini')

class Node:
	def __init__(self, name: str = 'Lambo'):
		self.name = name
		## information for every node
		self.ring = []
		self.current_transactions = []
		self.all_nodes_utxos = {}
		self.total_block_time = 0
		self.received_first_transaction = False
		self.chain = Blockchain()
		self.id = -1

	def set_ip_and_port(self, ip, port):
		self.ip = ip
		self.port = port

	def set_chain(self, c: Blockchain):
		self.chain = deepcopy(c)

	def set_name(self, n: str):
		self.name = n

	def set_ring(self, r):
		self.ring = r
		## id must be updated like this because it is defined by the boostrap
		for i in self.ring:
			if(i.wallet.public_key == self.wallet.public_key):
				self.set_id(i.id)

	def set_id(self, id: int):
		self.id = id

	def generate_wallet(self):
		## create a wallet for this node, with a public key and a private key
		self.wallet = Wallet()

	def get_wallet(self):
		return self.wallet

	def as_dict(self):
		temp = {
			'id': self.id,
			'name': self.name,
			'ip': self.ip,
			'port': self.port,
			'wallet': deepcopy(self.wallet.as_dict())
		}
		return temp

	def __eq__(self, other):
		## TODO not sure if this is correct
		return self.wallet.public_key == other.wallet.public_key

	## must be defined, it is not implied that ne = not eq
	def __ne__(self, other):
		return not self.__eq__(other)

	def register_bootstrap(self):
		"""
		should create initial transaction and block
		and also save boot ip
		and also save itself to ring
		"""
		self.id = 0
		self.wallet.utxos.append(
			{
				'transaction_hash': 0,
				'amount': 100 * int(config['EXPERIMENTS']['NODES']),
				'recipient_public_key': self.wallet.public_key
			}
		)
		self.ring.append(deepcopy(self))

	## send registration request to bootstrap node's address
	def send_registration_request(self):
		requests.post('http://127.0.0.1:5000/bootstrap/registerNode', json = json.dumps(self.as_dict()))

	## add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
	## bootstrap node informs all other nodes and gives the request node an id and 100 NBCs
	def register_node_to_ring(self, new_node):
		## public_key = n['wallet']['public_key']
		## ip = n['ip']
		## port = n['port']
		public_key = new_node.wallet.public_key
		ip = new_node.ip
		port = new_node.port
		try:
			if(self.id == 0):
				## Do not insert again on duplicate request
				for n in self.ring:
					## if(n['wallet']['public_key'] == public_key):
					if(n.wallet.public_key == public_key):
						raise Exception("Cannot register a node that has been registered already")
				## accepted
				new_node.set_id(len(self.ring))
				self.ring.append(new_node)
				'''
				if(len(self.ring) == int(config['EXPERIMENTS']['NODES'])):
					self.initialize_network()
				else:
					print(f"Not enough nodes yet, I have {len(self.ring)} and expect {config['EXPERIMENTS']['NODES']}")
				'''
			else: raise Exception("Only bootstrap can register nodes")
		except Exception as e:
			print(e)


	## create initial transaction to boostrap and genesis block
	def create_genesis(self):
		## self.create_transaction(self.wallet.public_key, 100 * int(config['EXPERIMENTS']['NODES']))
		## create seminal transaction manually not with the function I can't
		## be bothered to fix it
		t = Transaction(
			sender_public_key = self.wallet.public_key,
			sender_private_key = self.wallet.private_key,
			recipient_public_key = self.wallet.public_key,
			amount = 100 * int(config['EXPERIMENTS']['NODES']),
			transaction_inputs = None
		)
		t.transaction_hash = 0
		self.current_transactions.append(t)
		if(len(self.current_transactions) == int(config['EXPERIMENTS']['BLOCK_CAPACITY'])):
			temp = deepcopy(self.current_transactions)
			self.mine_block(temp, self.chain)
			self.current_transactions = []

		b = self.mine_block(
			tl = deepcopy(self.current_transactions),
			c = self.chain,
			g = True,
			leading_zeroes = int(config['EXPERIMENTS']['MINING_DIFFICULTY'])
		)
		B = Blockchain()
		B.add_block(b)
		self.chain = B

	## send complete ring to all nodes
	def initialize_network(self):
		if(not len(self.ring) == int(config['EXPERIMENTS']['NODES'])):
			print('NOT ENOUGH NODES')
			return
		print('ENOUGH NODES - INITIALIZING NETWORK')
		self.ring.sort(key = lambda x: x.id)
		for n in self.ring:
			if(n.id == 0): continue
			request_url = f'http://{n.ip}:{n.port}/node/ring'
			r = deepcopy(self.ring)
			serializable = [x.as_dict() for x in r]
			requests.post(request_url, json = json.dumps({'ring': serializable}))
			sleep(5)

	## send first block with genesis transaction
	## create transactions and broadcast them
	def send_genesis(self):
		## self.broadcast_block()
		self.broadcast_chain()
		for n in self.ring:
			if(n.id == 0): continue
			self.create_transaction(n.wallet.public_key, 100)
			## TODO there might be an issue with flushing the list
			self.broadcast_transaction(self.current_transactions[-1])

	## one ring to rule them all
	def update_rings(self):
		if(self.id != 0):
			raise Exception('Operation only allowed to the boostrap node')
		for n in self.ring:
			## TODOOOO!!! AAAAAAAAAAAAAAAA WITH REQUEST WHEN I BROADCAST TO ALL NODES
			request_url = f'http://{n.ip}:{n.port}/node/ring'
			r = deepcopy(self.ring)
			serializable = [x.as_dict() for x in r]
			requests.post(request_url, json = json.dumps({'ring': serializable}))

	## After a transaction has been created, it must be broadcast by `broadcast_transaction`
	def create_transaction(self, recipient_public_key, amount: float) -> Transaction:
		print(f'I am {self.name} and my atxos are')
		print(self.wallet.utxos)
		## TODO check if recipient address exists
		if(amount <= 0):
			raise Exception("Invalid amount")
		## Checking upon reception is different this is for a transaction that is broadcast
		## Determine source of "Inputs"
		utxo_sum = 0
		transaction_inputs = [] ## list of used utxos
		for utxo in self.wallet.utxos:
			transaction_inputs.append(utxo)
			utxo_sum += utxo['amount']
			if(utxo_sum >= amount): break

		## find sender and recipient in ring - will be useful later
		sender_in_ring = None
		recipient_in_ring = None
		for n in self.ring:
			if(n.wallet.public_key == recipient_public_key):
				recipient_in_ring = n
			if(n.wallet.public_key == self.wallet.public_key):
				sender_in_ring = n

		## remove utxos from inputs, the change will be returned as output of the new transaction
		for utxo in transaction_inputs:
			self.wallet.utxos.remove(utxo)

		## Validation is for receved transactions not sent
		t = Transaction(self.wallet.get_public_key(), self.wallet.private_key, recipient_public_key, amount, transaction_inputs)
		t.sign_transaction(self.wallet.private_key)

		## create outputs
		t.transaction_outputs = [
			{
				'transaction_hash': t.transaction_hash,
				'amount': t.amount,
				'recipient_public_key': t.recipient_public_key
			},
			{
				'transaction_hash': t.transaction_hash,
				'amount': utxo_sum - t.amount,
				'recipient_public_key': t.sender_public_key
			}
		]

		## update personal atxo in wallet
		## and both atxos in ring
		self.wallet.utxos.append(t.transaction_outputs[1])
		recipient_in_ring.wallet.utxos.append(t.transaction_outputs[0])
		self.ring.remove(sender_in_ring)
		self.ring.append(deepcopy(self))
		self.ring.sort(key = lambda x: x.id)

		self.current_transactions.append(t)
		if(len(self.current_transactions) == int(config['EXPERIMENTS']['BLOCK_CAPACITY'])):
			temp = deepcopy(self.current_transactions)
			self.mine_block(temp, self.chain)
			self.current_transactions = []
		## TODO I do not know what this does
		## self.wallet.transactions.append(t)
		## self.all_trans_ids.add(t.transaction_id)
		## TODO!!! append to list and increment counter
		## if at capacity mine
		print(f'I, {self.name}, created the following transaction:\n{t}')
		return t


	## Utility broadcast function, broadcasts a general message to every other node
	## TODO use thread pool maybe
	def broadcast(self, message, urlparam):
		## headers of http post request
		## headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
		for n in self.ring:
			## exclude current node
			if (n.wallet.public_key == self.wallet.public_key): continue
			## create URL for target node
			request_url = f'http://{n.ip}:{n.port}/{urlparam}'
			requests.post(request_url, json = message) ##, headers = headers)

	def broadcast_transaction(self, t: Transaction):
		self.broadcast(message = json.dumps(t.as_dict()), urlparam = 'transaction')

	def broadcast_block(self, b: Block):
		self.broadcast(message = json.dumps(b.as_dict()), urlparam = 'block')

	def broadcast_chain(self):
		self.broadcast(message = json.dumps(self.chain.as_dict()), urlparam = 'chain')

	def mine_block(self, tl: [Transaction], c: Blockchain, g: bool, leading_zeroes: int) -> Block:
		b = Block(genesis = g, previous_hash = c.get_latest_block_hash(), list_of_transactions = tl)
		for t in tl:
			## the importance of deepcopy
			b.add_transaction(t)
		start = perf_counter()
		hash = b.__hash__() ## nonce is initialized to 0
		## TODO str might be a bug
		while(not str(hash).startswith('0' * leading_zeroes)): ## condition not met
			b.nonce += 1 ## try next nonce
			hash = b.__hash__()
		end = perf_counter()
		print('mined block')
		self.total_block_time += end - start
		b.hash = hash
		return b

	## Upon receiving transaction
	def receive_transaction(self, t: Transaction):
		if(self.validate_transaction(t)):
			## if enough transactions mine
			if(not self.received_first_transaction):
				self.received_first_transaction = True
				self.timestamp_of_first_transaction = perf_counter()
			self.timestamp_of_latest_transaction = perf_counter()
			self.current_transactions.append(t)
			if(len(self.current_transactions) == int(config['EXPERIMENTS']['BLOCK_CAPACITY'])):
				temp = deepcopy(self.current_transactions)
				self.mine_block(temp, self.chain)
				self.current_transactions = []
		else:
			print('Transaction rejected')

	## TODO I have no idea what this does just fking copied it
	## Please find out
	def verify_signature(self, t: Transaction) -> bool:
		key = RSA.import_key(t.sender_public_key)
		h = t.generate_transaction_hash()
		signature = t.signature
		try:
			pkcs1_15.new(key).verify(h, signature)
			print("The signature is valid.")
			return True
		except (ValueError, TypeError) as e:
			print(e)
		return False

	def validate_transaction(self, t: Transaction) -> bool:
		## transaction to self not allowed, initial bootstrap transaction not validated
		if(t.recipient_public_key == t.sender_public_key):
			print('rejected because of same sender and recipient')
			return False

		## find sender and recipient in ring - will be useful later
		sender_in_ring = None
		recipient_in_ring = None
		for i in self.ring:
			if(i.wallet.public_key == t.sender_public_key):
				sender_in_ring = i
			if(i.wallet.public_key == t.recipient_public_key):
				recipient_in_ring = i
		print(f'SENDER IN RING: {sender_in_ring.as_dict()}\nRECIPIENT: {recipient_in_ring.as_dict()}')
		## Insufficient funds
		if(sender_in_ring.wallet.balance() < t.amount):
			print('rejected for insufficient funds')
			return False
		print('according to my data the sender has')
		print(sender_in_ring.wallet.utxos)
		print('his inputs')
		print(t.transaction_inputs)
		print('his outputs are')
		print(t.transaction_outputs)
		## signature and inputs - outputs
		if(not self.verify_signature(t)):
			print('rejected because of signature')
			return False
		'''
		for utxo in t.transaction_inputs:
			if(not utxo in sender_in_ring.wallet.utxos):
				print('rejected for atxos')
				return False
		'''
		for utxo in t.transaction_inputs:
			print(f'atxo to remove:\n{utxo}')
			sender_in_ring.wallet.utxos.remove(utxo)

		print(f'sender is {sender_in_ring.name}\nrecipient is {recipient_in_ring.name}\nand I am {self.name}')
		if(self == recipient_in_ring):
			print('this transaction was to me')
			self.wallet.utxos.append(t.transaction_outputs[0])

		recipient_in_ring.wallet.utxos.append(t.transaction_outputs[0])
		sender_in_ring.wallet.utxos.append(t.transaction_outputs[1])

		print(f'NOW AFTER TRANSACTION SENDER HAS {sender_in_ring.wallet.utxos}')
		print(f'NOW AFTER TRANSACTION RECIPIENT HAS {recipient_in_ring.wallet.utxos}')

		return True

	## Upon receiving block
	def receive_block(self, b: Block):
		match self.validate_block(b):
			case 0: ## reject
				pass
			case 1:
				self.resolve_conflict()
			case 2:
				self.add_block_to_chain(b)

	def validate_block(self, b: Block) -> int:
		"""
		0: invalid
		1: conflict
		2: valid
		"""
		## genesis block need not be validated
		if(self.genesis):
			return 2
		## check that the incoming block has a valid hash
		if(b.__hash__() != b.hash):
			return 1
		## check that the incoming block's previous hash is the last hash of the chain
		if(b.previous_hash != self.chain.get_latest_block_hash()):
			return 0
		## validate all transactions in block
		## keep backup because validate_transaction alters it
		all_nodes_utxos_backup = deepcopy(self.all_nodes_utxos)
		for t in b.list_of_transactions:
			if(not self.validate_transaction(t)):
				print('Transaction validation failed - block rejected')
				self.all_nodes_utxos = all_nodes_utxos_backup
				return 0

		## validate proof of work
		if(not self.validate_proof_of_work(b, config['EXPERIMENTS']['MINING_DIFFICULTY'])):
			return 0
		return 2

	def add_block_to_chain(self, b: Block):
		self.current_transactions = [x for x in self.current_transactions if x not in b.list_of_transactions]
		self.chain.add_block(b)

	def receive_chain(self, c: Blockchain):
		## if(self.validate_chain(c)):
		self.chain = c
		## TODO pretend to validate

	## For a new node entering the network
	## Run validate_block on entire chain
	def validate_chain(self, c: Blockchain):
		for b in c.chain:
			if(not (self.validate_block(b) == 2)):
				return False
		return True

	## TODO mining diff param
	def validate_proof_of_work(self, b: Block, diff: int) -> bool:
		return str(b.hash).startswith('0' * diff)

	def get_chain(self) -> Blockchain:
		return self.chain.as_dict()

	## consensus functions
	## also maybe thread pool
	## TODO what if I don't find it
	def resolve_conflict(self):
		max_chain = self.chain
		max_length = len(self.chain)
		for n in self.ring:
			if(n.get_wallet().get_public_key() == self.wallet.get_public_key()):
				continue
			request_url = f'http://{n.ip}:{n.port}/node/chain'
			res = requests.get(request_url)
			if(res.status_code != 200):
				raise Exception('Invalid response')

			## TODO this will not work but I'd rather fix it by trial and error than think how to do it
			received_chain = res['chain']
			received_chain_length = received_chain.get_length()
			if(self.validate_chain(res) and received_chain_length > max_length):
				max_length = received_chain_length
				max_chain = res
		self.chain = max_chain

	def get_statistics(self):
		number_of_valid_transactions = len(self.chain) * config['EXPERIMENTS']['BLOCK_CAPACITY']
		return {
			'average_block_time': self.total_block_time / len(self.chain),
			'throughput': number_of_valid_transactions / (self.timestamp_of_latest_transaction - self.timestamp_of_first_transaction)
		}
