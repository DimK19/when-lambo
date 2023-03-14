from collections import OrderedDict
import time
import json
from copy import deepcopy
import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
import requests
from flask import Flask, jsonify, request, render_template
import base64

class Transaction:

    def __init__(self, sender_address, sender_private_key, recipient_address, amount, transaction_inputs):
        ## To public key του wallet από το οποίο προέρχονται τα χρήματα
        self.sender_address = sender_address
        ## Για την υπογραφή που θα αποδεικνύει ότι ο κάτοχος του wallet δημιούργησε αυτό το transaction
        self._sender_private_key = sender_private_key
        ## To public key του wallet στο οποίο θα καταλήξουν τα χρήματα
        self.recipient_address = recipient_address
        ## το ποσό που θα μεταφερθεί
        self.amount = amount
        ## for measurements
        self.timestamp = time.time()
        #self.transaction_inputs: λίστα από Transaction Input
        self.transaction_inputs = transaction_inputs
        #self.transaction_outputs: λίστα από Transaction Output
        self.generate_transaction_hash()

    def __str__(self):
        try:
            return f'TRANSACTION {self.transaction_hash}\nSENDER: {self.sender_address}\nRECIPIENT: {self.recipient_address}\nAMOUNT:{self.amount}'
        except Exception as e:
            print('Cannot print unsigned transaction')
    '''
    @staticmethod
    def hashable_utxo(t):
        return {
            'transaction_id': str(t.transaction_hash),
            'type' : 0,
            'recipient': str(t.recipient_address),
            'amount': t.amount
        }

    def _hashable(self):
        return {
            'sender_address': str(self.sender_address),
            '_sender_private_key': str(self._sender_private_key),
            'recipient_address': str(self.recipient_address),
            'amount': self.amount,
            'timestamp': self.timestamp,
            'transaction_inputs': map(Transaction.hashable_utxo, self.transaction_inputs)
        }
    '''
    def generate_transaction_hash(self):
        """
        Hash the entire object to produce the id
        """
        ## TODO I have no idea whether this works or even is correct
        self.transaction_hash = SHA256.new(json.dumps(self.__dict__, default = vars).encode('ISO-8859-2')).hexdigest()

    def sign_transaction(self, sender_private_key):
        """
        Sign transaction with private key
        """
        ##object_hash = SHA256.new(data = self.transaction_hash.encode())
        ##signer = PKCS1_v1_5.new(sender_private_key)
        ##self.signature = base64.b64encode(signer.sign(object_hash))
        ## return self.signature
        message = self.transaction_hash.encode("ISO-8859-1")
        key = RSA.importKey(sender_private_key.encode("ISO-8859-1"))
        h = SHA256.new(message)
        signer = PKCS1_v1_5.new(key)
        self.signature = signer.sign(h).decode('ISO-8859-1')
        return self.signature
