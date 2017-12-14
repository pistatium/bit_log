# coding: utf-8

import os, json

import requests
import python_bitbankcc

API_KEY = os.environ['BITBANK_API_KEY']
API_SECRET = os.environ['BITBANK_API_SECRET']
SLACK_WEBHOOK = os.environ['SLACK_WEBHOOK']

public_api = python_bitbankcc.public()
private_api = python_bitbankcc.private(API_KEY, API_SECRET)

pair_cache = {}

convertable = {
    'btc': 'jpy',
    'xrp': 'jpy',
    'ltc': 'btc',
    'eth': 'btc',
    'mona': 'jpy',
    'bcc': 'jpy'
}

def get_jpy_rate(from_asset):
    if from_asset == 'jpy':
        return 1.0
    to_asset = convertable[from_asset]
    pair = f'{from_asset}_{to_asset}'
    cached = pair_cache.get(pair)
    if cached:
        return cached
    result = public_api.get_ticker(pair)
    rate = float(result['last'])
    pair_cache[pair] = rate
    return rate * get_jpy_rate(to_asset)

def post_slack(text):
    requests.post(SLACK_WEBHOOK, json={
        'channel': '#test',
        'text': text
    })


def main():
    result = private_api.get_asset()
    assets = result['assets']
    sum = 0
    for asset in assets:
        name = asset['asset']
        amount = float(asset['onhand_amount'])
        if amount <= 0:
            continue
        yen = int(get_jpy_rate(name) * amount)
        sum += yen
        print(f'{name}\t{amount}\t{yen}')
    print(f'Sum: {sum}')
    if SLACK_WEBHOOK:
        post_slack(str(sum))

if __name__ == '__main__':
    main()
