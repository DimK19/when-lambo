import concurrent.futures
import requests
import configparser
from time import perf_counter, sleep

config = configparser.ConfigParser()
config.read('constants.ini')

addresses = [
'http://127.0.0.1:5000',
'http://127.0.0.1:2000',
'http://127.0.0.1:3000',
'http://127.0.0.1:4000',
'http://127.0.0.1:6000'
]

requests.get('http://127.0.0.1:2000/node/register')
requests.get('http://127.0.0.1:3000/node/register')
requests.get('http://127.0.0.1:4000/node/register')
requests.get('http://127.0.0.1:6000/node/register')
requests.get('http://127.0.0.1:5000/bootstrap/initialize')
sleep(10)

def foo(url):
    requests.get(url)

start = perf_counter()
responses = []
with concurrent.futures.ThreadPoolExecutor(max_workers = int(config['EXPERIMENTS']['NODES'])) as executor:
    ##for i in addresses:
    ##    executor.submit(foo, i + '/experiment')
    future_to_url = (executor.submit(foo, url + '/experiment') for url in addresses)
    for future in concurrent.futures.as_completed(future_to_url):
        try:
            data = future.result()
            responses.append(data)
        except Exception as e:
            print(e)
    ## https://superfastpython.com/threadpoolexecutor-wait-all-tasks/
    concurrent.futures.wait(future_to_url)
    end = perf_counter()
    print(f'Finished conducting experiment in {end - start}s')

    for i in addresses:
        executor.submit(foo, i + '/node/stats')
    print('Saved results to text files')
