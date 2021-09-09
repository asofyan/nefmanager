# NEF Manager

by: asofyan@gmail.com

Python app to manage your trades by using Nefertiti Bot from command line. Nefertiti is cool cryptocurrency trading bot made by @svanas, see here: https://nefertiti-tradebot.com/ for more information. Basically the bot will find the best support available, put a limit buy on it and wait. After limit buy take place, the sell bot will automatically set sell with specific target profit. The default is 5%. This is default setting for everything. You can adjust the bot to match your criteria.

Nefertiti, for simplicity, only provides command line, lack of management tool. This software is trying to provides the management with the main feature:
1. Start, stop, and restart your NEF bot.
2. See the status of your bot
3. Logviewer (todos)
4. Summary of PnL (todos)

As it first published to match my need, this tool equipped with automatically coin picking from Trending coins.

## Installation
1. Copy config.cfg.txt to config.cfg
2. Edit your configuration. To add new exchange, add section in your config. You may copy from [binance] section
3. Please make sure you edit `prices`
4. Create virtual environment for nefman (*optional*) `virtualenv .envnefman`
5. Enter your virtual environment `source .envnefman/bin/activate`
6. Install requirements with pip `pip install -f requirements.txt`
7. Run setup.py `python setup.py`
8. Create log folder `mkdir logs sell` for sell logs folder, `mkdir -p logs/{binance,kucoin,hitbtc}` for buy logs per exchange. Please change to your exchanges
8. Get the pairs for active exchange to be used (eg. get list of active market on Binance)-> `python exchangemarket.py -e BINANCE`   
   This step used to make sure the pair exists in your exchange (even nef also checked that), and for checking if you want to run random pairs for trending coins.
9. This optional steps, is getting trending coin from livecoinwatch.com, from rank 51-100. I assume in that rank, the coins is trending, but have no momentum yet, with enough volume (avoid shitcoins). Before run this step, make sure you register API for free in livecoinwatch. You may edit the source code to match your rank. Do this to get trending coins -> `python lcmarket.py`

We are ready to trade with Nef.

## Trading
1. Run sell bot `python nefman.py -e BINANCE -a startsell`. The output will be available as log file in `sell` folder. 
2. Run buy bot `python nefman.py -e BINANCE -a buy -m ETHUSDT`. The output will be available as log file in `logs\{exchange}` folder
3. Stop the bot `python nefman.py -e BINANCE -a stop -m ETHUSDT`. It will delete log file in `logs\binance\ETHUSDT` as well.
4. Trading summary `python nefman.py -e BINANCE -a summary`
5. List of active bots `python nefman.py -e BINANCE -a list`
Tips: -e or exchange can set default in nefman.py file, so you don't have to write it everytime

## Maintenance
No maintenance necessary. But if you want to start a system, this is what I have been doing. This is my trading system, set in cron job. If you don't like it, don't run it. Use your own system.
1. Every x days (default to 3 days), check if there's enough transactions
2. If not, shutdown the bot. Close all buy limits. Market sell any sell limit
3. Regularly calculate the pl summary based on transaction data (x days)
4. Update the balance based on PL summary  (x days)


## Requirements
All requirements is already noted in requirements.txt. Use pip to install them all.
1. Python3
2. PeeWee ORM
3. Sqlite - default. You can change it

Tested on Mac and Linux Ubuntu

