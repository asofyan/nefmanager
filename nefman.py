#!/usr/bin/env python
import configparser, datetime
import subprocess, os, sys, time, signal
from optparse import OptionParser

import peewee
from models import *

config = configparser.RawConfigParser()
config.read('config.cfg')
nefcon = config['nefmanager']


class nefMan:
    exchange = 'BINANCE'
    market = None
    botconf = {} # pass the config.cfg values
    instances = {'USDT':3, 'BTC': 3, 'ETH':3, 'BUSD': 3, 'BNB':3}
    quotes = ['USDT','BUSD','BTC','ETH','BNB']
    cryptotrader = 'cryptotrader' # full path of cryptotrader bin
    params = [] # holding bot parameters
    sandbox = False # set it to true to only display command without really executing it

    def __init__(self, exchange='BINANCE'):    
        print("starting nefman..")
        self.exchange = exchange
        #self.set_instances()

    # different exchange config rather than binance
    def set_instances(self,botconf):
        self.botconf = botconf
        exconf = self.botconf[self.exchange.lower()]
        params = [
            self.cryptotrader,
            '--exchange=%s'%self.exchange.upper(),
            '--api-key=%s'%exconf['api_key'],
            '--api-secret=%s'%exconf['api_secret'],
            '--telegram-app-key=%s'%self.botconf['bot']['telegram_key'],
            '--telegram-chat-id=%s'%self.botconf['bot']['telegram_id'],
            '--pushover-app-key=%s'%self.botconf['bot']['pushover_app_key'],
            '--pushover-user-key=%s'%self.botconf['bot']['pushover_user_key'],
            '--ignore-error'
        ]
        self.params = params
        #if self.exchange.lower() in self.botconf:
        
        print("instances",exconf['bot_instances'], exconf['quotes'])
        self.instances = eval(exconf['bot_instances'])
        self.quotes = eval(exconf['quotes'])
        

    def start(self):
        print('run buy nefbot')
        #print(self.params)
        # update the trending coin first
        cdir = os.getcwd()
        if not self.sandbox and not self.market:
            pass
            # we do this and check aggregation on separate process
            #lcmarket = os.path.join(cdir,'lcmarket.py')
            #p = subprocess.Popen([lcmarket],shell=True)
            # allow market to be updated
            #time.sleep(10)
        
        # we got lists of random trending pairs
        try:
            ex = Exchange.get(Exchange.name == self.exchange)
        except:
            ex = False
        buyparam = self.params
        buyparam.insert(1,'buy')
        buyparam.append('--repeat=%s'%self.botconf['bot']['repeat'])
        prices = eval(self.botconf[self.exchange.lower()]['prices'])
        
        # market defined, executed only single NEF buy
        if self.market:
            mark = Markets.get(Markets.exchange == ex, Markets.name == self.market)
            if mark:
                if self.market[-4:] in ['USDT','BUSD']:
                    buyparam.append('--price=%s'%prices[self.market[-4:]])
                else:
                    price_str = '--price=%s'%prices[self.market[-3:]]
                    buyparam.append(price_str)
                buyparam.append('--market=%s'%self.market)
                logfile = os.path.join(cdir, 'logs', self.market)
                try:
                    traded = TradedPairs.get(
                        TradedPairs.exchange == ex, 
                        TradedPairs.pairs == self.market, 
                        TradedPairs.active == True)
                    print("active trading is still going for %s"%self.market)
                except:
                    if self.sandbox:
                        print(" ".join(buyparam),' > ', logfile, '2>&1')
                    else:
                        p = subprocess.Popen(['%s > %s 2>&1'%(" ".join(buyparam),logfile)], shell=True)
                        traded = TradedPairs()
                        traded.exchange = ex
                        traded.pairs = self.market
                        traded.active = True
                        traded.pid = p.pid
                        traded.save()
                        print("successfully start %s NEF bot at %s"%(self.market, ex.name))
            else:
                print("Market %s not found in %s"%(self.market, ex.name))
            sys.exit()
            # stop here for specific market
        # for every pairs, we check through available market
        mtanks = '' # avoid double by checking in this array
        for qt in self.quotes:
            qparam = buyparam[:]
            qparam.append('--price=%s'%prices[qt])
            print('--')
            #print(qparam)
            self.instances[qt] = int(self.instances[qt])
            trends = Trending.select(Trending.code)\
                    .where(Trending.active==True, Trending.counter>0)\
                    .order_by(fn.Random()).limit(30)
            for tr in trends:
                if ex:
                    market = Markets.select().where(Markets.exchange == ex, Markets.name.contains(tr.code))
                    for mk in market:
                        cparam = qparam[:]
                        #print(qparam)
                        #print('market %s'%mk.name)
                        if qt in mk.name and self.instances[qt]>0 and tr.code not in mtanks:
                            self.instances[qt] = self.instances[qt]-1
                            mtanks = mtanks + mk.name
                            try:
                                traded = TradedPairs.get(
                                    TradedPairs.exchange == ex, 
                                    TradedPairs.pairs == mk.name, 
                                    TradedPairs.active == True)
                                break
                            except:
                                print("NEF bot %s %s"%(mk.name,tr.code))
                                logfile = os.path.join(cdir, 'logs', mk.name)
                                cparam.append('--market=%s'%mk.name)
                                if self.sandbox:
                                    #pass
                                    print(" ".join(cparam),' > ',logfile,'2>&1')
                                else:
                                    p = subprocess.Popen(['%s > %s 2>&1'%(" ".join(cparam),logfile)], shell=True)
                                    traded = TradedPairs()
                                    traded.exchange = ex
                                    traded.pairs = mk.name
                                    traded.active = True
                                    traded.pid = p.pid
                                    traded.save()
                                #cparam.clear()
                                break
                        #cparam.clear()
            #qparam.clear()



    def stop(self):
        print('stop nef bot')
        try:
            ex = Exchange.get(Exchange.name == self.exchange)
        except e:
            print("failed to get exchange")
            ex = False
        if ex:
            print("stopping instance")
            # no pair provided, delete all
            if not self.market:
                print("no pair.. get all active %s"%(ex.name))
                traded = TradedPairs.select().where(TradedPairs.exchange == ex, TradedPairs.active == True)
                for t in traded:
                    stopparams = self.params[:]
                    stopparams.insert(1,'cancel')
                    stopparams.append('--market=%s'%t.pairs)
                    stopparams.append('--side=buy')
                    print(t.pid)
                    if self.sandbox:
                        print("rm -rf %s"%(os.path.join(os.getcwd(),'logs',t.pairs)))
                    else:
                        try:
                            os.kill(t.pid+1, signal.SIGTERM)
                            t.end_date = datetime.datetime.now()
                            t.active = False
                            t.save()
                            # cancel all buys order
                            p = subprocess.Popen([" ".join(stopparams)],shell=True)
                            try:
                                os.remove(os.path.join(os.getcwd(),'logs',t.pairs))
                            except:
                                print("Error delete log file logs/%s"%t.pairs)
                        except Exception as e:
                            print("Failed to kill %s %s %s"%(t.pid, t.pairs, e))
            else:
                if self.sandbox:
                    print("rm -rf %s"%(os.path.join(os.getcwd(),'logs',self.market)))
                else:
                    try:
                        traded = TradedPairs.get(TradedPairs.exchange == ex, 
                                TradedPairs.pairs == self.market, 
                                TradedPairs.active == True)
                        os.kill(traded.pid+1, signal.SIGTERM)
                        traded.end_date = datetime.datetime.now()
                        traded.active = False
                        traded.save()
                        stopparams = self.params
                        stopparams.insert(1,'cancel')
                        stopparams.append('--market=%s'%self.market)
                        stopparams.append('--side=buy')
                        print(" ".join(stopparams))
                        subprocess.Popen([" ".join(stopparams)], shell=True)
                        try:
                            os.remove(os.path.join(os.getcwd(),'logs',self.market))
                        except:
                            print("Error delete log file logs/%s"%self.market)
                    except Exception as e:
                        print("Failed to kill %s: %s"%(self.market, e))

        
    def startsell(self):
        print("starting selling bot")
        self.__check_nef()
        sellparam = self.params
        sellparam.insert(1,'sell')
        sellparam.append('--strategy=%s'%self.botconf['bot']['strategy'])
        sellparam.append('--mult=%s'%self.botconf['bot']['mult'])
        if self.exchange.upper() == 'BINANCE':
            sellparam.append('--quote=%s'%",".join(self.quotes))
        curdir = os.getcwd()
        logfile = os.path.join(curdir, 'sell', 'sell-%s.log'%self.exchange.lower())
        if self.sandbox:
            print(" ".join(sellparam),'>',logfile,'2>&1')
        else:
            p = subprocess.Popen(['%s > %s 2>&1'%(" ".join(sellparam),logfile)], shell=True)
            f = open(os.path.join(curdir,'sell','sell.pid'),'w')
            # save pid for future close or restart
            f.write(str(p.pid))
            f.close()


    def __check_nef(self):
        curdir = os.getcwd()
        try:
            self.cryptotrader = os.path.join(curdir,'cryptotrader')
            return True
        except:
            print("can't find cryptotrader. Please download nefertiti and set the correct path")
            return False

    def listnef(self):
        print('list existing nef bot and pids')

    def summary(self):
        print('summary PnL of existing bot')

    # check existing bots
    # check the number
    def restart(self):
        print('restart all bots')

pars = OptionParser()
pars.add_option('-e', '--exchange')
pars.add_option('-a','--action')
pars.add_option('-m','--market')
option, remain = pars.parse_args(sys.argv[1:])

if __name__ == '__main__':
    startnef = False
    stopnef = False
    startsell = False
    if option.exchange:
        exchange = option.exchange
    else:
        exchange = 'BINANCE'
    if option.action:
        action = option.action
        if action == 'buy':
            startnef = True
        if action == 'stop':
            stopnef = True
        if action == 'sell':
            startsell = True
    nef = nefMan(exchange)
    nef.sandbox = False # debugging only
    nef.set_instances(config)
    if option.market:
        nef.market = option.market
    if startnef:
        nef.start()
    if stopnef:
        nef.stop()
    if startsell:
        nef.startsell()