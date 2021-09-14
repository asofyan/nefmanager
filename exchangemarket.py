#!/usr/bin/env python
import configparser, datetime
import subprocess, os, sys
from optparse import OptionParser

import peewee
from models import *

config = configparser.RawConfigParser()
config.read('config.cfg')
nefcon = config['nefmanager']
exchanges = [
    {'name': 'BINANCE','quotes': ['USDT','BUSD','BTC','ETH','BNB']},
    {'name': 'HITBTC','quotes': ['USD','BTC','ETH']},
    {'name': 'KUCOIN','quotes': ['USDT','BTC','ETH']}
]

def get_market(exchange,quotes):
    curdir = os.getcwd()
    try:
        command = os.path.join(curdir,'cryptotrader')
    except:
        print("can't find cryptotrader. Please download nefertiti and set the correct path")
    #output = subprocess.check_output("%s --help"%command)
    output = subprocess.check_output([command,'markets','--exchange=%s'%exchange])
    markets = eval(output.decode('utf-8'))
    # check if exchange already exists
    try:
        exc = Exchange.get(Exchange.name==exchange)
    except:
        exc = Exchange()
        exc.name = exchange
        exc.save()

    for mar in markets:
        for q in quotes:
            if q in mar['name']:
                try:
                    #already exist, ignore it
                    quote = Markets.get(Markets.exchange==exc, Markets.name == mar['name'])
                except:
                    # create new one
                    quote = Markets()
                    quote.exchange = exc
                    quote.name = mar['name']
                    quote.agg = 0.0
                    quote.save()
                print(mar['name'])


pars = OptionParser()
pars.add_option('-e', '--exchange')
option, remain = pars.parse_args(sys.argv[1:])

if __name__ == '__main__':
    exchange = exchanges[0]['name'] # binance
    quotes = exchanges[0]['quotes']
    if option.exchange:
        exchange = option.exchange
        for e in exchanges: # get quotes from the exchanges
            if exchange == e['name']:
                quotes = e['quotes']
    get_market(exchange, quotes)