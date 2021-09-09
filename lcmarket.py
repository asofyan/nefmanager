#!/usr/bin/env python
import configparser, datetime
from coinmarketcapapi import CoinMarketCapAPI, CoinMarketCapAPIError
import requests
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json, sys
import peewee
from models import *

config = configparser.RawConfigParser()
config.read('config.cfg')
nefcon = config['nefmanager']

url = 'https://api.livecoinwatch.com/coins/list'
parameters = {
    'currency':'USD',
    'sort':'volume',
    'order': 'descending',
    'offset': 50,
    'limit':50,
    'meta': 'false'
}
headers = {
  'content-type': 'application/json',
  'x-api-key': nefcon['lc_api_key'],
}

if __name__ == '__main__':
    #ex = 'BINANCE'
    ex = 1
    response = requests.post(url,headers=headers,data=json.dumps(parameters))
    datas = json.loads(response.text)
    db.connect()

    # set every pair to false, updated = now
    trends = Trending.select()
    for trend in trends:
        trend.active = False
        trend.save()
    for data in datas:
        #print(data['code'],data['volume'])
        # update trending data:
        try:
            t = Trending.get(Trending.code == data['code'])
            print("update %s"%data['code'])
            # any existing pair, update counter+1, active=True, updated = now
            t.volume = data['volume']
            t.updated = datetime.datetime.now()
            t.active = True
            t.counter = t.counter + 1
            t.save()
        except:
            print("new %s"%data['code'])
            t = Trending()
            t.code = data['code']
            t.volume = data['volume']
            t.counter = 0
            t.save()
    
    # delete fiat and NFT, add more exclusion here
    coin_excluded = ['USD','_','PAX','DAI','DGX','IDR','UP','DOWN','HT','KCS']
    for ce in coin_excluded:
        fiat = Trending.delete().where(Trending.code.contains(ce))
        fiat.execute()

    # delete 5 coins that inactive, order by created
    try:
        inactive = Trending.delete().where(Trending.active == False).order_by(Trending.created).limit(5)
        inactive.execute()
    except:
        print("All actives")

    # get random pairs for binance
    print("get pair for binance")
    trends = Trending.select(Trending.code).where(Trending.active==True, Trending.counter>0).order_by(fn.Random()).limit(12)
    for tr in trends:
        print("--")
        market = Markets.select().where(Markets.exchange == ex, Markets.name.contains(tr.code))
        #print(market)
        for mk in market:
            print(mk.name)
        