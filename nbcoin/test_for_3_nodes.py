## A SCRIPT THAT AUTOMATES STANDARD SETUP OPERATIONS FOR TESTING
import requests
from time import sleep
from sys import argv

if(len(argv) == 2 and argv[1] == 'i'):
    requests.get('http://127.0.0.1:2000/node/register')
    requests.get('http://127.0.0.1:3000/node/register')
    requests.get('http://127.0.0.1:5000/bootstrap/initialize')
    sleep(30)
    ## 100 100 100

requests.get('http://127.0.0.1:2000/transaction/create')
sleep(1)
requests.get('http://127.0.0.1:2000/transaction/create')
sleep(1)
## 120 60 120

requests.get('http://127.0.0.1:3000/transaction/create')
sleep(1)
## 130 70 100

requests.get('http://127.0.0.1:5000/transaction/create')
sleep(1)
## 110 80 110

requests.get('http://127.0.0.1:5000/transaction/create')
sleep(1)
## 90 90 120

requests.get('http://127.0.0.1:3000/transaction/create')
sleep(1)
## 100 100 100

requests.get('http://127.0.0.1:5000/transaction/create')
sleep(1)
## 80 110 110

requests.get('http://127.0.0.1:5000/transaction/create')
sleep(1)
## 60 120 120

requests.get('http://127.0.0.1:2000/transaction/create')
sleep(1)
## 70 100 130

requests.get('http://127.0.0.1:2000/transaction/create')
sleep(1)
## 80 80 140

requests.get('http://127.0.0.1:3000/transaction/create')
sleep(1)
## 90 90 120

requests.get('http://127.0.0.1:3000/transaction/create')
sleep(1)
## 100 100 100
