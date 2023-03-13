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

@app.route('/node/register', methods = ['POST'])
def register_node(is_boot = True, name = 'Countach'):
    ## is_boostrap inside request
    N.set_name(name)
    N.generate_wallet()
    N.register_bootstrap()
    ## else register node if not bootstrap
    print(N.__dict__)
    return {}


## run it once fore every node
if(__name__ == '__main__'):
    ## parser = ArgumentParser()
    ## parser.add_argument('-p', '--port', default = 5000, type=int, help='port to listen on')
    ## args = parser.parse_args()
    ## port = args.port
    app.run(host = '127.0.0.1', port = 5000, debug = True) ## =port)

'''
change blockchain from none to empty
save confing of bootstrap ip to register other nodes
finalize node registration
move on to transactioan
transaction val error messages
'''
