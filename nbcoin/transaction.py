from collections import OrderedDict
import time
import json
from copy import deepcopy
import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5, pkcs1_15
import requests
from flask import Flask, jsonify, request, render_template
import base64

class Transaction:

    def __init__(
        self,
        sender_public_key,
        sender_private_key,
        recipient_public_key,
        amount,
        transaction_inputs,
        transaction_outputs = None,
        signature = None,
        transaction_hash = None,
        timestamp = None
    ):
        ## To public key του wallet από το οποίο προέρχονται τα χρήματα
        self.sender_public_key = sender_public_key
        ## Για την υπογραφή που θα αποδεικνύει ότι ο κάτοχος του wallet δημιούργησε αυτό το transaction
        self.sender_private_key = sender_private_key
        ## To public key του wallet στο οποίο θα καταλήξουν τα χρήματα
        self.recipient_public_key = recipient_public_key
        ## το ποσό που θα μεταφερθεί
        self.amount = amount
        ## for measurements
        self.timestamp = time.time() if timestamp is None else timestamp
        ## self.transaction_inputs: λίστα από Transaction Input
        self.transaction_inputs = transaction_inputs
        ## self.transaction_outputs: λίστα από Transaction Output
        self.transaction_outputs = transaction_outputs
        ## αυτό και το προηγούμενο τα έχω για τον constructor στο endpoint που
        ## χρησιμοποιεί τα δεδομένα του request
        if(signature is not None):
            self.signature = bytes(signature, 'ISO-8859-2')
        else:
            self.signature = None
        self.transaction_hash = transaction_hash
        self.generate_transaction_hash()

    def __str__(self):
        try:
            return f'TRANSACTION {self.transaction_hash}\nSENDER: {self.sender_public_key}\nRECIPIENT: {self.recipient_public_key}\nAMOUNT:{self.amount}\nINPUTS:{self.transaction_inputs}\nOUTPUTS:{self.transaction_outputs}'
        except Exception as e:
            print('Cannot print unsigned transaction')

    def as_dict(self):
        res = {k: self.__dict__[k] for k in self.__dict__ if(not k == 'signature')}
        ## special case for seminal transaction
        if(self.signature is not None):
            res['signature'] = self.signature.decode('ISO-8859-2')
        else:
            res['signature'] = '0'
        return res

    def generate_transaction_hash(self):
        """
        Hash the entire object to produce the id
        """
        ## TODO I have no idea whether this works or even is correct
        ## transaction outputs cannot be included since they contain the hash itself
        desired_keys = [
            'sender_public_key',
            'sender_private_key',
            'recipient_public_key',
            'amount',
            'timestamp'
        ]
        td = sorted([str(self.__dict__[k]) for k in desired_keys])
        self.transaction_hash = SHA256.new(json.dumps(td, default = vars).encode('ISO-8859-2')).hexdigest()
        return SHA256.new(json.dumps(td, default = vars).encode('ISO-8859-2'))

    def sign_transaction(self, sender_private_key):
        """
        Sign transaction with private key
        """
        '''
        object_hash = SHA256.new(data = self.transaction_hash.encode())
        signer = PKCS1_v1_5.new(sender_private_key)
        self.signature = base64.b64encode(signer.sign(object_hash))
        return self.signature
        '''
        key = RSA.import_key(self.sender_private_key)
        h = self.generate_transaction_hash()
        self.signature = pkcs1_15.new(key).sign(h)
        return self.signature
