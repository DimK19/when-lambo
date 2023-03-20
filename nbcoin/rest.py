import requests
from argparse import ArgumentParser
import json
import configparser
from time import sleep
from random import random
from copy import deepcopy

from flask import Flask, jsonify, request, make_response
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

config = configparser.ConfigParser()
config.read('constants.ini')

## @app.route('/bootstrap/registerSelf', methods = ['POST'])
def register_bootstrap():
    ## is_boostrap inside request
    ## name from request object
    N.set_name('Countach')
    N.set_ip_and_port('127.0.0.1', 5000)
    N.generate_wallet()
    N.register_bootstrap()
    ## else register node if not bootstrap
    return {}

## vm creates node and sends registration request
## @app.route('/node/create', methods = ['POST'])
def create_node(name, ip, port):
    ## is_boostrap inside request
    ## name from request object
    ##name = request.form.get(name)
    ##ip = request.form.get(ip)
    ##port = request.form.get(port)
    N.set_name(name)
    N.set_ip_and_port(ip, port)
    N.generate_wallet()
    ## N.send_registration_request()
    ## else register node if not bootstrap
    return {}

@app.route('/node/register', methods = ['GET'])
def send_registration_request():
    N.send_registration_request()
    return {}

def recreate_node(data):
    n = Node(data['name'])
    n.set_id(data['id'])
    n.set_ip_and_port(data['ip'], data['port'])
    n.wallet = Wallet()
    n.wallet.private_key = data['wallet']['private_key']
    n.wallet.public_key = data['wallet']['public_key']
    n.wallet.utxos = data['wallet']['utxos']
    return n

## bootstrap node receives request and registers node
@app.route('/bootstrap/registerNode', methods = ['POST'])
def register_node():
    data = json.loads(request.get_json(force = True))
    n = recreate_node(data)
    '''
    n = Node(data['name'])
    n.set_ip_and_port(data['ip'], data['port'])
    n.wallet = Wallet()
    n.wallet.private_key = data['wallet']['private_key']
    n.wallet.public_key = data['wallet']['public_key']
    '''
    N.register_node_to_ring(n)
    return {}

@app.route('/bootstrap/initialize', methods = ['GET'])
def init_network():
    N.initialize_network()
    N.create_genesis()
    N.send_genesis()
    return {}

## receive ring from bootstrap upon initialization
@app.route('/node/ring', methods = ['POST'])
def receive_ring():
    request_data = json.loads(request.get_json(force = True))
    r = request_data['ring']
    r = list(map(recreate_node, r))
    N.set_ring(r)
    return {}

## return chain of node for conflict resolution
@app.route('/node/chain', methods = ['GET'])
def return_chain():
    return N.get_chain()

## testing
@app.route('/test', methods = ['GET'])
def test():
    print(N.ring)
    print(N.name)
    return {}

## testing
@app.route('/transaction/test', methods = ['GET'])
def transactiontest():
    return make_response(jsonify(json.dumps([t.as_dict() for t in N.current_transactions])), 200)

## testing
@app.route('/transaction/create', methods = ['GET'])
def othertest():
    ## I will run this as id = 1 Murcielago
    ## and try to send 50 to the two others
    for i in N.ring:
        if(i.id != N.id):
            recipient_public_key = i.wallet.public_key
            try:
                t = N.create_transaction(recipient_public_key, amount = 10)
                N.broadcast_transaction(t)
            except Exception as e:
                pass
    return make_response({}, 200)

## testing
@app.route('/node/test', methods = ['GET'])
def test3():
    return make_response(jsonify(json.dumps({'name': N.name, 'balance': N.wallet.balance()})), 200)

## testing
@app.route('/node/test4', methods = ['GET'])
def test4():
    return make_response(jsonify(json.dumps({'response': str(N.chain)})), 200)

## receive transaction
@app.route('/transaction', methods = ['POST'])
def receive_transaction():
    request_data = json.loads(request.get_json(force = True))
    t = Transaction(**request_data)
    N.receive_transaction(t)
    return make_response({}, 200)

## receive block
@app.route('/block', methods = ['POST'])
def receive_block():
    request_data = json.loads(request.get_json(force = True))
    tl = []
    for i in request_data['list_of_transactions']:
        tl.append(Transaction(**i))
    request_data['list_of_transactions'] = tl
    b = Block(**request_data)
    N.receive_block(b)
    return make_response({}, 200)

## receive chain
@app.route('/chain', methods = ['GET', 'POST'])
def receive_chain():
    ## IF METHOD IS POST, CREATE BLOCKCHAIN OBJECT AND SET IT AS NODES CHAIN
    if(request.method == 'POST'):
        request_data = json.loads(request.get_json(force = True))
        bc = []
        for b in request_data['chain']:
            tl = []
            for i in b['list_of_transactions']:
                tl.append(Transaction(**i))
            b['list_of_transactions'] = tl
            bc.append(Block(**b))
        c = Blockchain(bc)
        N.receive_chain(c)
        return make_response({}, 200)
    ## ELSE IF METHOD IS GET, RETURN CHAIN
    else:
        return make_response(jsonify(json.dumps(N.chain.as_dict())), 200)

## ------------------------------------------------------------------------------------------------
## OPERATIONS REQUIRED FOR CLI
@app.route('/node/transaction/create', methods = ['POST'])
def create_transaction():
    request_data = json.loads(request.get_json(force = True))
    recipient_public_key = request_data['recipient_public_key']
    amount = request_data['amount']
    try:
        t = N.create_transaction(recipient_public_key, amount = amount)
        N.broadcast_transaction(t)
        return make_response(jsonify(json.dumps(t.as_dict())), 200)
    except Exception as e:
        print(e)
        return make_response({}, 422)
        ## https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/422

@app.route('/node/transaction/view', methods = ['GET'])
def view_transactions():
    res = {'chain': N.chain.as_dict(), 'str': N.chain.view_transactions()}
    return make_response(jsonify(json.dumps(res)), 200)

@app.route('/node/balance', methods = ['GET'])
def get_balance():
    res = {'balance': N.wallet.balance()}
    return make_response(jsonify(json.dumps(res)), 200)

@app.route('/node/info', methods = ['GET'])
def get_information():
    res = {'info': str(N)}
    return make_response(jsonify(json.dumps(res)), 200)

@app.route('/node/stats', methods = ['GET'])
def get_statistics():
    return make_response(jsonify(json.dumps(N.get_statistics())), 200)
    ## https://flask.palletsprojects.com/en/2.2.x/api/#flask.make_response
    ## https://flask.palletsprojects.com/en/2.2.x/api/#flask.json.jsonify

## ------------------------------------------------------------------------------------------------
## FOR EXPERIMENTS FROM TEXT FILES
@app.route('/experiment', methods = ['GET'])
def conduct_experiment():
    n = int(config['EXPERIMENTS']['NODES'])
    id_to_key = {}
    for i in N.ring:
        id_to_key[i.id] = i.wallet.public_key
    with open(f'../transactions/{n}nodes/transactions{N.id}.txt') as f:
        for line in f:
            recipient_id, amount = line.split()
            recipient_public_key = id_to_key[int(recipient_id)]
            amount = float(amount)
            try:
                t = N.create_transaction(recipient_public_key, amount)
                N.broadcast_transaction(t)
                sleep(6 * random()) ## mean 5 minutes for 100 transactions
            except Exception as e:
                ## print(e)
                pass
    return make_response({}, 200)

## ------------------------------------------------------------------------------------------------
## FOR GUI
@app.route('/node', methods = ['GET'])
def get_node():
    return make_response(jsonify(json.dumps(deepcopy(N.as_dict()))), 200)

@app.route('/ring', methods = ['GET'])
def get_ring():
    res = deepcopy({'ring': [x.as_dict() for x in N.ring]})
    return make_response(jsonify(json.dumps(res)), 200)

## run it once fore every node
## TODO!! DIFFERENTIATE BETWEEN BOOTSTRAP AND OTHERS IN A BETTER WAY
if(__name__ == '__main__'):
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default = 5000, type = int)
    parser.add_argument('-i', '--host', default = '127.0.0.1', type = str)
    parser.add_argument('-n', '--name', default = 'Lambo', type = str)
    args = parser.parse_args()
    host = args.host
    port = args.port
    name = args.name
    if(port != 5000): create_node(name, host, port)
    else: register_bootstrap()
    app.run(host = host, port = port)
    ## LIFESAVER https://stackoverflow.com/a/16664376
    ## https://requests.readthedocs.io/en/latest/api/#lower-level-classes

'''
change blockchain from none to empty
save confing of bootstrap ip to register other nodes
finalize node registration
move on to transactioan
transaction val error messages
'''
