from copy import deepcopy
from block import Block
from wallet import Wallet
from transaction import Transaction
from blockchain import Blockchain

class Node:
	def __init__(self, name: str = 'Lambo'):
		self.name = name
		## information for every node
		self.ring = []
		self.current_transactions = []
		self.utxos_of_others = {}

	def set_chain(self, c: Blockchain):
		self.chain = deepcopy(c)

	def set_name(self, n: str):
		self.name = n

	def generate_wallet(self):
		## create a wallet for this node, with a public key and a private key
		self.wallet = Wallet()

	def get_wallet(self):
		return self.wallet

	def register_bootstrap(self):
		"""
		should create initial trasnaction and block
		and also save boot ip
		and also save itself to ring
		"""
		## TODO!!! amount
		self.wallet.utxos.append({'transaction_id': 0, 'type': 0, 'recipient': self.wallet.get_public_key(), 'amount': 500})
		self.create_transaction(self.wallet.public_key, 500) ## config with number of nodes
		b = self.mine_block(None, True, 2)
		B = Blockchain()
		B.add_block(b)
		self.chain = B
		self.ring.append(self)


	## add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
	## bootstrap node informs all other nodes and gives the request node an id and 100 NBCs
	def register_node_to_ring(self, n):
		public_key = n.get_wallet().get_public_key()
		ip = n.get_ip()
		port = n.get_port()
		try:
			if(self.id == 0):
				## Do not insert again on duplicate request
				for n in self.ring:
					if(n.public_key == public_key):
						raise Exception("Cannot register a node that has been registered already")
				self.ring.append({"public_key": public_key, "ip": ip, "port": port, "balance": 0})
				return len(self.ring)
			else: raise Exception("Only bootstrap can register nodes")
		except Exception as e:
			print(e)

	## one ring to rule them all
	def update_rings(self):
		if(self.id != 0):
			raise Exception('Operation only allowed to the boostrap node')
		for n in self.ring:
			n.ring = deepcopy(self.ring)

	## After a transaction has been created, it must be broadcast by `broadcast_transaction`
	def create_transaction(self, recipient_address, amount: float):
		## TODO check if recipient_address exists
		if(amount <= 0): raise Exception("Invalid amount")
		## Checking upon reception is different this is for a transaction that is broadcast
		## Determine source of "Inputs"
		utxo_sum = 0
		transaction_inputs = [] ## list of used utxos
		for utxo in self.wallet.utxos:
			transaction_inputs.append(utxo)
			utxo_sum += utxo['amount']
			if(utxo_sum >= amount): break

		## remove utxos from inputs, the change will be returned as output of the new transaction
		for utxo in transaction_inputs:
			self.wallet.utxos.remove(utxo)

		## Validation is for receved transactions not sent
		t = Transaction(self.wallet.get_public_key(), self.wallet.private_key, recipient_address, amount, transaction_inputs)
		t.sign_transaction(self.wallet.private_key)

		## create outputs
		transaction_outputs = [
			{
				'transaction_hash': t.transaction_hash,
				'type' : 0,
				'recipient': t.recipient_address,
				'amount': t.amount
			},
			{
				'transaction_hash': t.transaction_hash,
				'type' : 1,
				'recipient': t.sender_address,
				'amount': utxo_sum - t.amount
			}
		]

		self.current_transactions.append(t)
		## TODO I do not know what this does
		## self.wallet.transactions.append(t)
		## self.all_trans_ids.add(t.transaction_id)
		## TODO!!! append to list and increment counter
		## if at capacity mine

	## Utility broadcast function, broadcasts a general message to every other node
	## TODO use thread pool maybe
	def broadcast(self, message, urlparam):
		## headers of http post request
		headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
		for n in self.ring:
			## exclude current node
			if (n.id == self.id): continue
			## create URL for target node
			nodeURL = ""
			requests.post(nodeURL + "/" + urlparam, data = m, headers = headers)

	def broadcast_transaction(self, t: Transaction):
		self.broadcast(message = json.dumps(t.__dict__), urlparam = 'transaction')

	def broadcast_block(self, b: Block):
		self.broadcast(message = json.dumps(b.__dict__), urlparam = 'block')

	def mine_block(self, c: Blockchain, g: bool = False, leading_zeroes: int = 4) -> Block:
		b = Block(chain = c, genesis = g)
		for t in self.current_transactions:
			b.add_transaction(t)
		hash = b.calculate_block_hash() ## nonce is initialized to 0
		## TODO str might be a bug
		while(not str(hash).startswith('0')): ## condition not met
			b.nonce += 1 ## try next nonce
			hash = b.calculate_block_hash()
		b.hash = hash
		return b

	## Upon receiving transaction
	def receive_transaction(self, t: Transaction):
		if(self.validate_transaction(t)):
			## if enough transactions mine
			self.current_block.add_transaction(t)
		else:
			print('Transaction rejected')

	## TODO I have no idea what this does just fking copied it
	## Please find out
	def verify_signature(self, t: Transaction):
		RSAkey = RSA.importKey(t.sender_address.encode())
		verifier = PKCS1_v1_5.new(RSAkey)
		return verifier.verify(t.transaction_id, base64.b64decode(t.signature))

	def validate_transaction(self, t: Transaction) -> bool:
		## transaction to self not allowed, initial bootstrap transaction not validated
		if(recipient_address == self.wallet.public_key):
			return False
		## Insufficient funds
		if(t.get_recipient_address().get_wallet().balance() < amount):
			return False
		## signature and inputs - outputs
		if(not self.verify_signature(t)):
			return False
		for utxo in t.transaction_inputs:
			if(not utxo in all_nodes_utxos[t.sender_address]):
				return False
		for utxo in t.transaction_inputs:
			all_nodes_utxos[t.sender_address].remove(utxo)
		all_nodes_utxos[t.recipient_address].append(t.transaction_outputs[0])
		all_nodes_utxos[t.sender_address].append(t.transaction_outputs[1])
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
		if(b.generate_block_hash() != b.hash):
			return 1
		## check that the incoming block's previous hash is the last hash of the chain
		if(b.previous_hash != self.chain.get_latest_block_hash()):
			return 0
		return 2

	def add_block_to_chain(self, b: Block):
		self.chain.add_block(b)

	## For a new node entering the network
	## Run validate_block on entire chain
	def validate_chain(self, c: Blockchain):
		for b in c.chain:
			if(not (self.validate_block(b) == 2)):
				return False
		return True

	## TODO mining diff param
	def validate_proof_of_work(self, b: Block, diff: int = 4) -> bool:
		return str(b.hash).startswith('0' * diff)

	def get_chain(self) -> Blockchain:
		return self.chain

	## consensus functions
	## also maybe thread pool
	## TODO what if I don't find it
	def resolve_conflict(self):
		max_chain = self.chain
		max_length = len(self.chain)
		for n in self.ring:
			if(n.get_wallet().get_public_key() == self.wallet.get_public_key()):
				continue
			request_url = ''
			res = requests.get(request_url)
			if(res.status_code != 200):
				raise Exception('Invalid response')

			## TODO this will not work but I'd rather fix it by trial and error than think how to do it
			received_chain_length = res.get_length()
			if(self.validate_chain(res) and received_chain_length > max_length):
				max_length = received_chain_length
				max_chain = res
		self.chain = max_chain
