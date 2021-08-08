#!/usr/bin/env python
import configparser, datetime
import subprocess, os, sys
from optparse import OptionParser

import peewee
from models import *

config = configparser.RawConfigParser()
config.read('config.cfg')
nefcon = config['nefmanager']


def update_agg(exchange, market = None):
    curdir = os.getcwd()
    try:
        command = os.path.join(curdir,'cryptotrader')
    except:
        print("can't find cryptotrader. Please download nefertiti and set the correct path")
    try:
        ex = Exchange.get(Exchange.name==exchange)
    except:
        ex = False
    if market:
        p = subprocess.check_output([command,'agg','--market=%s'%market,'--exchange=%s'%exchange])
        if eval(p)>0:
            print(p)
            if ex:
                update = Markets.get(Markets.exchange == ex, Markets.name == market)
                update.agg = eval(p)
                update.updated = datetime.datetime.now()
                update.save()
    else:
        marks = Markets.select().order_by(Markets.updated).limit(10)
        for m in marks:
            try:
                p = subprocess.check_output([command,'agg','--market=%s'%m.name,'--exchange=%s'%exchange])
                if eval(p)>0:
                    print(m.name, eval(p))
                    m = Markets.update(agg = eval(p),updated=datetime.datetime.now()).where(Markets.name == m.name, Markets.exchange == ex)
                    m.execute()
            except:
                mu = Markets.update(updated=datetime.datetime.now()).where(Markets.name == m.name, Markets.exchange == ex)
                mu.execute()
                print("Failed to get aggregate %s, update only "%m.name)



pars = OptionParser()
pars.add_option('-e', '--exchange')
pars.add_option('-m','--market')
option, remain = pars.parse_args(sys.argv[1:])

if __name__ == '__main__':
    exchange = 'BINANCE'
    if option.exchange:
        exchange = option.exchange.upper()
    market = False
    if option.market:
        market = option.market
    if not market:
        #print("usage updateagg.py -e EXCHANGE_NAME -m MARKET_NAME")
        update_agg(exchange)
    else:
        update_agg(exchange, market)