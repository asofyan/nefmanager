# installation
import os, datetime
import configparser
from models import *
import subprocess

# creating tables
print("creating tables ..")
db.connect()
tables = [Trending, Exchange, Markets, TradedPairs, Transaction]
for t in tables:
    alltables = db.get_tables()
    if t not in alltables:
        db.create_tables([t])

print("import new fresh trending coins")
curdir = os.getcwd()
lcmarket = os.path.join(curdir, 'lcmarket.py')
os.system(lcmarket)
# fill default for binance
# use exchangemarket -m KUCOIN etc. Exchange must be supported by NEF
print("import exchange market")
bina = os.path.join(curdir,'exchangemarket.py')
os.system(bina)
