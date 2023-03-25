import concurrent.futures
import requests
import configparser
from time import perf_counter, sleep

config = configparser.ConfigParser()
config.read('constants.ini')

## FOR LOCAL TESTING

addresses = [
'http://127.0.0.1:5000',
'http://127.0.0.1:2000',
'http://127.0.0.1:3000',
'http://127.0.0.1:4000',
'http://127.0.0.1:6000'
]
"""
addresses = [
'http://192.168.0.5:5000',
'http://192.168.0.1:2000',
'http://192.168.0.2:3000',
'http://192.168.0.3:4000',
'http://192.168.0.4:6000'
]
"""

requests.get(addresses[1] + '/node/register')
sleep(1)
requests.get(addresses[2] + '/node/register')
sleep(1)
requests.get(addresses[3] + '/node/register')
sleep(1)
requests.get(addresses[4] + '/node/register')
sleep(1)
requests.get(addresses[0] + '/bootstrap/initialize')
sleep(10)

def foo(url):
    requests.get(url)

start = perf_counter()
responses = []
with concurrent.futures.ThreadPoolExecutor(max_workers = int(config['EXPERIMENTS']['NODES'])) as executor:
    future_to_url = (executor.submit(foo, url + '/experiment') for url in addresses)
    for future in concurrent.futures.as_completed(future_to_url):
        try:
            data = future.result()
            responses.append(data)
        except Exception as e:
            print(e)
    ## https://superfastpython.com/threadpoolexecutor-wait-all-tasks/
    ## concurrent.futures.wait(future_to_url)
    end = perf_counter()
    print(f'Finished conducting experiment in {end - start}s')
