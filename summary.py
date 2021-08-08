#!/usr/bin/env python
# asofyan@gmail.com
# summary.py - simple script to parse NEF Sell log into PnL

import configparser, datetime
import subprocess, os, sys, time, signal, json
from decimal import Decimal
from optparse import OptionParser

pars = OptionParser()
pars.add_option('-f', '--file')


def summary(filepath):
        cdir = os.getcwd()
        summary = {}
        with open(filepath,'r') as logs:
            for log in logs:
                lines = log.split() 
                if 'FILLED' in lines[2]:
                    data = json.loads(lines[3])
                    #data["%s_%s"%(data['side'],data['symbol'])] += amount
                    amount = Decimal(data['price'])*Decimal(data['executedQty']) 
                    if data['symbol'] not in summary:
                        summary[data['symbol']] = 0
                    if data['side'] == 'BUY':
                        summary[data['symbol']] = summary[data['symbol']] - amount
                    if data['side'] == 'SELL':
                        summary[data['symbol']] = summary[data['symbol']] + amount                    
                    print(lines[0],data['symbol'],data['side'],data['price'],data['executedQty'],amount)
                    #print(data['symbol'])
                    #print(data['side'])
                    #print(data['price'])
                    #print(data['executedQty'])
        logs.close()
        print(summary)
        
        #for l in eval(logs):
        #    print(l)
        sys.exit()

if __name__ == '__main__':
    option, remain = pars.parse_args(sys.argv[1:])
    if not option.file:
        print("usage: summary.py -f full/log/file/path")
    else:
        summary(option.file)