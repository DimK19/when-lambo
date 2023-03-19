## A SCRIPT THAT AUTOMATES STANDARD SETUP OPERATIONS FOR TESTING
import requests
from time import sleep

requests.get('http://127.0.0.1:2000/node/register')
requests.get('http://127.0.0.1:3000/node/register')
requests.get('http://127.0.0.1:4000/node/register')
requests.get('http://127.0.0.1:6000/node/register')
requests.get('http://127.0.0.1:5000/bootstrap/initialize')
sleep(30)
## 100 100 100 100 100

requests.get('http://127.0.0.1:2000/transaction/create')
sleep(1)
requests.get('http://127.0.0.1:2000/transaction/create')
sleep(1)
## 120 20 120 120 120

requests.get('http://127.0.0.1:3000/transaction/create')
sleep(1)
## 130 30 80 130 130

requests.get('http://127.0.0.1:5000/transaction/create')
sleep(1)
## 90 40 90 140 140

requests.get('http://127.0.0.1:5000/transaction/create')
sleep(1)
## 50 50 100 150 150

requests.get('http://127.0.0.1:3000/transaction/create')
sleep(1)
## 60 60 60 160 160

requests.get('http://127.0.0.1:4000/transaction/create')
sleep(1)
## 70 70 70 120 170

requests.get('http://127.0.0.1:4000/transaction/create')
sleep(1)
## 80 80 80 80 180

requests.get('http://127.0.0.1:6000/transaction/create')
sleep(1)
## 90 90 90 90 140

requests.get('http://127.0.0.1:6000/transaction/create')
sleep(1)
## 100 100 100 100 100

requests.get('http://127.0.0.1:6000/transaction/create')
sleep(1)
## 110 110 110 110 60
