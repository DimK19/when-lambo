from flask import render_template, redirect, url_for, request, flash, abort
from client import app
## from flask_login import login_user, current_user, logout_user, login_required
import os
import requests
import json

## node simply as dict from response for the purposes of this app
N = None
ring = None

### Αρχική Σελίδα ###
@app.route('/home/')
## @login_required
def home():
    return render_template('index.html', name = N['name'])


## Σελίδα Λογαριασμού Χρήστη με δυνατότητα αλλαγής των στοιχείων του
## Να δοθεί ο σωστός decorator για υποχρεωτικό login
@app.route('/account/', methods = ['GET'])
##@login_required
def account():
    global N
    data = {'id': N['id'], 'name': N['name'], 'ip': N['ip'], 'port': N['port']}
    return render_template('node_info.html', name = N['name'], data = data)


### Σελίδα Login ###
@app.route('/login/', methods = ['GET', 'POST'])
@app.route('/')
def login():
    global N, ring
    '''
    if(current_user.is_authenticated):
        return redirect(url_for('home'))
    '''
    ## form = LoginForm() ## Αρχικοποίηση φόρμας Login

    if(request.method == 'POST'):## and form.validate_on_submit()):
        address = request.form.get('address')
        res = requests.get(address + '/node')
        N = json.loads(res.json())
        res = requests.get(address + '/ring')
        ring = json.loads(res.json())['ring']
        return redirect(url_for('home'))
    else:
        return render_template('login.html')


### Σελίδα Logout ###
@app.route('/logout/')
def logout():
    ## Αποσύνδεση Χρήστη
    ## logout_user()
    ## flash('Έγινε αποσύνδεση του χρήστη.', 'success')
    ## Ανακατεύθυνση στην αρχική σελίδα
    return redirect(url_for('login'))


@app.route('/wallet/', methods = ['GET', 'POST'])
##@login_required
def wallet():
    public_key = N['wallet']['public_key'].replace('-----BEGIN PUBLIC KEY-----', '') \
        .replace('-----END PUBLIC KEY-----', '') \
        .replace('\n', '') \
        .strip()

    private_key = N['wallet']['private_key'].replace('-----BEGIN RSA PRIVATE KEY-----', '') \
        .replace('-----END RSA PRIVATE KEY-----', '') \
        .replace('\n', '') \
        .strip()

    request_url = f"http://{N['ip']}:{N['port']}/node/balance"
    response = requests.get(request_url)
    balance = json.loads(response.json())['balance']

    return render_template(
        'wallet.html',
        name = N['name'],
        public_key = public_key,
        private_key = private_key,
        balance = balance
    )


@app.route('/blockchain/', methods = ['GET'])
##@login_required
def blockchain():
    request_url = f"http://{N['ip']}:{N['port']}/node/transaction/view"
    response = requests.get(request_url)
    if(response.status_code == 200):
        data = json.loads(response.json())
        list_of_transactions = data['chain']['chain'][-1]['list_of_transactions']
    return render_template('blockchain.html', name = N['name'], list_of_transactions = list_of_transactions)


@app.route('/transaction/', methods = ['GET', 'POST'])
##@login_required
def transaction():
    global N, ring
    if(request.method == 'GET'):
        ## populate list of options
        node_data = []
        for i in ring:
            if(i['id'] == N['id']):
                continue
            node_data.append({'id': int(i['id']), 'name': i['name'], 'public_key': i['wallet']['public_key']})
        node_data.sort(key = lambda x: x['id'])
        ## also display balance while doing transaction
        request_url = f"http://{N['ip']}:{N['port']}/node/balance"
        response = requests.get(request_url)
        balance = json.loads(response.json())['balance']
        ## generate form
        return render_template('transaction.html', name = N['name'], node_data = node_data, balance = balance)
    else:
        recipient_public_key = request.form.get('recipient')
        recipient_public_key = recipient_public_key.replace('\n', '').replace('\r', '\n')
        ## recipient_public_key = recipient_public_key.replace('\r', '\n')
        amount = float(request.form.get('amount'))
        request_url = f"http://{N['ip']}:{N['port']}/node/transaction/create"
        response = requests.post(request_url, json = json.dumps({'recipient_public_key': recipient_public_key, 'amount': amount}))
        if(response.status_code == 200):
            flash('Transaction completed successfully', 'success')
        else:
            flash('Error', 'danger')
        return redirect(url_for('transaction'))
    ## else if post
    ## send request to nbc
    ## flash message
    ## redirect to transaction page
