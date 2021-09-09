#!/usr/bin/env python
import configparser, datetime
import subprocess, os, sys, time, signal, json
import requests
from decimal import Decimal
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
    active_pairs = [] # avoid to stop this coins where we do mass stopping

    def __init__(self, exchange='BINANCE'):    
        #print("starting nefman..")
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
        
        #print("instances",exconf['bot_instances'], exconf['quotes'])
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
                logfile = os.path.join(cdir, 'logs', ex.name.lower(), self.market)
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
            
            # update the instances by active instance
            existing_instances = TradedPairs.select().where(TradedPairs.exchange == ex,
                    TradedPairs.active == True, TradedPairs.pairs.contains(qt)).count()
            self.instances[qt] = int(self.instances[qt]) - int(existing_instances)
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
                                logfile = os.path.join(cdir, 'logs', ex.name.lower(), mk.name)
                                cparam.append('--market=%s'%mk.name)
                                if self.sandbox:
                                    #pass
                                    print(" ".join(cparam),' > ',logfile,'2>&1')
                                else:
                                    p = subprocess.Popen(['%s > %s 2>&1'%(" ".join(cparam),logfile)], shell=True)
                                    time.sleep(5)
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
        sys.exit()


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
                # select pair who have no transaction
                traded = TradedPairs.select().where(TradedPairs.exchange == ex, TradedPairs.active == True)
                self.summary(exit=False)
                print(self.active_pairs)
                if len(self.active_pairs) > 0 :
                    traded = traded.where(TradedPairs.pairs.not_in(self.active_pairs))
                for t in traded:
                    stopparams = self.params[:]
                    stopparams.insert(1,'cancel')
                    stopparams.append('--market=%s'%t.pairs)
                    stopparams.append('--side=buy')
                    #print(t.pid)
                    if self.sandbox:
                        print("rm -rf %s"%(os.path.join(os.getcwd(),'logs',ex.name.lower(),t.pairs)))
                    else:
                        try:
                            os.kill(t.pid+1, signal.SIGTERM)
                            t.end_date = datetime.datetime.now()
                            t.active = False
                            t.save()
                            # cancel all buys order
                            p = subprocess.Popen([" ".join(stopparams)],shell=True)
                            try:
                                os.remove(os.path.join(os.getcwd(),'logs',ex.name.lower(),t.pairs))
                            except:
                                print("Error delete log file logs/%s/%s"%(ex.name.lower(),t.pairs))
                        except Exception as e:
                            print("Failed to kill %s %s %s"%(t.pid, t.pairs, e))
            else:
                if self.sandbox:
                    print("rm -rf %s"%(os.path.join(os.getcwd(),'logs',ex.name.lower(), self.market)))
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
                            os.remove(os.path.join(os.getcwd(),'logs',ex.name.lower(),self.market))
                        except:
                            print("Error delete log file logs/%s/%s"%(ex.name.lower(),self.market))
                    except Exception as e:
                        print("Failed to kill %s: %s"%(self.market, e))
        sys.exit()

        
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
            f = open(os.path.join(curdir,'sell','sell-%s.pid'%self.exchange.lower()),'w')
            # save pid for future close or restart
            f.write(str(p.pid))
            f.close()
        sys.exit()


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
        active = TradedPairs.select().where(TradedPairs.active == True)
        summa = []
        for ac in active:
            buy = Transaction.select().where(Transaction.pair == ac.pairs, Transaction.sell== False).count()
            sell = Transaction.select().where(Transaction.pair == ac.pairs, Transaction.sell== True).count()
            summa.append({
                'pair': ac.pairs,
                'pid': ac.pid,
                'buy': buy,
                'sell': sell,
                'total': buy+sell,
            })
            #print(ac.pairs,ac.pid, "buy:",buy,"sell:",sell, 'total:', buy+sell)

        sorted_summa = sorted(summa, key=lambda k: k['total'],reverse=True)
        for s in sorted_summa:
            if s['total'] == 0:
                print("-",s['pair'],s['pid'],s['buy'],s['sell'],s['total'])
            else:
                print("+ ",s['pair'],s['pid'],s['buy'],s['sell'],s['total'])
        print('-------')
        print("total %s NEF BOTs"%len(sorted_summa))
        sys.exit()

    def summary(self, exit=True):
        cdir = os.getcwd()
        filepath = os.path.join(cdir,'sell','sell-%s.log'%self.exchange.lower())
        summary = {}
        sumqty = {}
        price = {} # get last price to calculate actual value. Not accurate
        qty = { 'binance':'executedQty' , 'hitbtc':'quantity'}
        with open(filepath,'r') as logs:
            for log in logs:
                lines = log.split() 
                if 'FILLED' in lines[2]:
                    data = json.loads(lines[3])
                    format_qty = data[qty[self.exchange.lower()]]
                    #data["%s_%s"%(data['side'],data['symbol'])] += amount
                    amount = Decimal(data['price'])*Decimal(format_qty)
                    if data['symbol'] not in summary:
                        summary[data['symbol']] = 0
                        sumqty[data['symbol']] = 0
                    if data['side'] == 'BUY':
                        summary[data['symbol']] = summary[data['symbol']] - amount
                        sumqty[data['symbol']] = sumqty[data['symbol']] + Decimal(format_qty)
                    if data['side'] == 'SELL':
                        summary[data['symbol']] = summary[data['symbol']] + amount  
                        sumqty[data['symbol']] = sumqty[data['symbol']] - Decimal(format_qty)
                    try:
                        trx = Transaction.get(Transaction.trxid == data['clientOrderId'])
                    except:
                        trx = Transaction()
                        trx.pair = data['symbol']
                        if data['side'] == 'BUY':
                            trx.sell = False
                        trx.amount = amount
                        trx.price = data['price']
                        trx.qty = format_qty
                        trx.trxid = data['clientOrderId']
                        trx.save()
                    print(lines[0],data['symbol'],data['side'],data['price'],format_qty,amount)
                    price[data['symbol']] = data['price']
                    #print(data['symbol'])
                    #print(data['side'])
                    #print(data['price'])
                    #print(data['executedQty'])
        logs.close()
        #print(summary)
        #print(sumqty)
        # now calculate floating PnL
        pairs = summary.keys()
        self.active_pairs = list(pairs)
        print("------")
        total_profit = 0
        # get latest data
        urlt = 'https://api.binance.com/api/v3/ticker/price?symbol='
        for p in pairs:
            if summary[p] > 0:
                print(p,' Profit: ', summary[p])
                if p[:-3] == 'ETH' or p[:-3] == 'BTC':
                    profit = balance + summary[p]
                else:
                    profit = balance + summary[p]
                total_profit = total_profit + summary[p]
            else:
                response = requests.get("%s%s"%(urlt,p))
                if self.exchange.lower() == 'binance':
                    price = json.loads(response.content)
                    balance = sumqty[p] * Decimal(price['price'])
                else:
                    # get last price
                    balance = sumqty[p] * Decimal(price[p])
                if p[:-3] == 'ETH' or p[:-3] == 'BTC':
                    quote = p[:-3]
                    if self.exchange.lower() == 'binance':
                        response = requests.get("%s%sUSDT"%(urlt,quote))
                        lprice = json.loads(response.content)
                        profit = (balance*Decimal(lprice['price'])) + summary[p]
                    else:
                        profit = (balance*Decimal(price[p])) * summary[p]
                else:
                    profit = balance + summary[p]
                print(p,'Profit: ',profit)
                total_proit = total_profit + profit
        print('-----')
        print(total_profit)
        if exit:
            sys.exit()

    def help(self):
        print("require action. See Readme.MD")

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
    if option.exchange:
        exchange = option.exchange
    else:
        exchange = 'BINANCE'
    nef = nefMan(exchange)
    nef.sandbox = True # debugging only
    nef.set_instances(config)
    if option.market:
        nef.market = option.market
    if option.action:
        action = option.action
        if action == 'buy':
            nef.start()
        if action == 'stop':
            nef.stop()
        if action == 'sell':
            nef.startsell()
        if action == 'summary':
            nef.summary()
        if action == 'list':
            nef.listnef()
    nef.help()
