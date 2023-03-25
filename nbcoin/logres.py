import requests

addresses = [
'http://127.0.0.1:5000/node/stats',
'http://127.0.0.1:2000/node/stats',
'http://127.0.0.1:3000/node/stats',
'http://127.0.0.1:4000/node/stats',
'http://127.0.0.1:6000/node/stats'
]

for i in addresses:
    requests.get(i)
print('Saved results to text files')
