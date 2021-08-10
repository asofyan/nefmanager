from peewee import *
import os, datetime
import configparser

config = configparser.RawConfigParser()
config.read('config.cfg')
nefcon = config['nefmanager']

db = SqliteDatabase(nefcon['sqlite'])

class Trending(Model):
    code = CharField()
    volume = IntegerField()
    created = DateTimeField(default=datetime.datetime.now)
    updated = DateTimeField(default=datetime.datetime.now)
    counter = IntegerField()
    active = BooleanField(default=True)

    class Meta:
        database =  db


class Exchange(Model):
    name = CharField(unique=True)

    class Meta:
        database =  db

class Markets(Model):
    exchange = ForeignKeyField(Exchange)
    name = CharField()
    agg = DecimalField()
    updated = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database =  db
        constraints = [SQL('UNIQUE (exchange_id, name)')]

class TradedPairs(Model):
    exchange = ForeignKeyField(Exchange)
    pairs = CharField()
    start_date = DateTimeField(default = datetime.datetime.now)
    end_date = DateTimeField(default = datetime.datetime.now)
    active = BooleanField(default=True)
    pid = IntegerField()

    class Meta:
        database =  db

class Transaction(Model):
    pair = ForeignKeyField(TradedPairs)
    trxid = CharField(null=True)
    date = DateTimeField(default = datetime.datetime.now)
    sell = BooleanField(default=True) # true = sell, false = buy
    amount = DecimalField()
    price = DecimalField(default=0.0)
    qty = DecimalField(default=0.0)

    class Meta:
        database =  db

