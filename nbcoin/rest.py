import requests
from argparse import ArgumentParser

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

from block import Block
from node import Node
from blockchain import Blockchain
from wallet import Wallet
from transaction import Transaction

app = Flask(__name__)
CORS(app)
## B = Blockchain()
N = Node()

## get all transactions in the blockchain
@app.route('/transactions', methods = ['GET'])
def get_transactions():
    print(N.__dict__)
    N.chain.view_transactions()
    ## response = {'transactions': transactions}
    ##return jsonify(response), 200
    return {}

@app.route('/bootstrap/registerSelf', methods = ['POST'])
def register_bootstrap():
    ## is_boostrap inside request
    ## name from request object
    N.set_name('Countach')
    N.set_ip_and_port('127.0.0.1', 5000)
    N.generate_wallet()
    N.register_bootstrap()
    ## else register node if not bootstrap
    print(N.__dict__)
    return {}

## vm creates node and sends registration request
@app.route('/node/create', methods = ['POST'])
def create_node():
    ## is_boostrap inside request
    ## name from request object
    N.set_name('Murcielago')
    N.set_ip_and_port('127.0.0.1', 6000)
    N.generate_wallet()
    N.send_registration_request()
    ## else register node if not bootstrap
    print(N.__dict__)
    return {}

## bootstrap node receives request and registers node
@app.route('/bootstrap/registerNode', methods = ['POST'])
def register_node():
    print('REQUEST')
    print(request.form)
    ## N.register_node_to_ring()
    return {}

## testing
@app.route('/node/test', methods = ['GET'])
def test():
    N.register_node_to_ring(request)

## run it once fore every node
if(__name__ == '__main__'):
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default = 5000, type = int)
    args = parser.parse_args()
    port = args.port
    app.run(host = '127.0.0.1', port = port, debug = True) ## =port)

'''
change blockchain from none to empty
save confing of bootstrap ip to register other nodes
finalize node registration
move on to transactioan
transaction val error messages
'''
