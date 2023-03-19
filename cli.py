import requests
from argparse import ArgumentParser
import json

parser = ArgumentParser()
parser.add_argument('-a', '--host', type = str)
parser.add_argument('-p', '--port', type = int)
args = parser.parse_args()
host = args.host
port = args.port
base_url = f'http://{host}:{port}/node'

HELP_MESSAGE = """
WHOAMI                                Displays the connected node's information.
T [RECIPIENT_ADDRESS] [AMOUNT]        Creates transaction of AMOUNT from you to RECIPIENT_ADDRESS (public key) and broadcasts it.
VIEW                                  Displays all transactions in the latest validated block.
BALANCE                               Displays your wallet's total funds.
STATS                                 Displays statistics for the wallet.
EXIT                                  Quits the N00BCOIN CLI program.
"""

while True:
    cli_input = input('N00BCOIN>').strip().split()
    if(not cli_input): continue
    if(cli_input[0].lower() == 'whoami' and len(cli_input) == 1):
        request_url = base_url + '/info'
        response = requests.get(request_url)
        if(response.status_code == 200):
            data = json.loads(response.json())
            print(data['info'])
        else:
            print(f'Error {response.status_code}')
    elif(cli_input[0].lower() == 't'):
        try:
            recipient_public_key = cli_input['1']
            amount = float(cli_input['2'])
        except ValueError as e:
            print('Invalid command. Type "help" for more information.')
            continue
        request_url = base_url + '/transaction/create'
        response = requests.post(request_url, json.dumps({'recipient_public_key': recipient_public_key, 'amout': amount}))
        if(response.status_code == 200):
            print('Success:')
            print(response)
        else:
            print(f'Error {response.status_code}')

    elif(cli_input[0].lower() == 'view' and len(cli_input) == 1):
        request_url = base_url + '/transaction/view'
        response = requests.get(request_url)
        if(response.status_code == 200):
            data = json.loads(response.json())
            print(data['str'])
        else:
            print(f'Error {response.status_code}')

    elif(cli_input[0].lower() == 'balance' and len(cli_input) == 1):
        request_url = base_url + '/balance'
        response = requests.get(request_url)
        if(response.status_code == 200):
            data = json.loads(response.json())
            print(f"Wallet funds: {data['balance']} NBC")
        else:
            print(f'Error {response.status_code}')

    elif(cli_input[0].lower() == 'stats' and len(cli_input) == 1):
        request_url = base_url + '/stats'
        response = requests.get(request_url)
        if(response.status_code == 200):
            data = json.loads(response.json())
            print(f"Average block time: {data['average_block_time']}\nThroughput: {data['throughput']}")
        else:
            print(f'Error {response.status_code}')

    elif(cli_input[0].lower() == 'help' and len(cli_input) == 1):
        print(HELP_MESSAGE)

    elif(cli_input[0].lower() == 'exit'):
        exit(0)

    else:
        print('Invalid command. Type "help" for more information.')
