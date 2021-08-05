# NEF Manager

by: asofyan@gmail.com

Python app to manage your trades by using Nefertiti Bot from command line. Nefertiti is cool cryptocurrency trading bot made by @svanas, see here: https://nefertiti-tradebot.com/ for more information. Basically the bot will find the best support available, put a limit buy on it and wait. After limit buy take place, the sell bot will automatically set sell with specific target profit. The default is 5%. This is default setting for everything. You can adjust the bot to match your criteria.

Nefertiti, at it finest, only provides command line, lack of management tool. This software is trying to provides the management with the main feature:
1. Start, stop, and restart your NEF bot.
2. See the status of your bot
3. Logviewer (todos)
4. Summary of PnL (todos)

As it first published to match my need, this tool equipped with automatically coin picking from Trending coins.

*Preparation*
1. Fill in the exchange data (example: Binance)
2. Get the pairs for active exchange to be used (eg. get list of active market on Binance)
3. Regularly update the list of any coins that match your criteria (from livecoin or coinmarketcap)

*Trading*
1. Get list of any chosen coins, compare with active pairs
2. Start the NEF with preconfigured settings
3. Record the transaction and summary

*Maintenance*
1. Every x days (default to 3 days), check if there's enough transactions
2. If not, shutdown the bot. Close all buy limits. Market sell any sell limit
3. Regularly calculate the pl summary based on transaction data (x days)
4. Update the balance based on PL summary  (x days)

**INSTALLATION**
1. Download Nefertiti and put in your executable path
1. copy config.cfg.txt to config.cfg
2. Adjust your settings. You must understand how Nefertiti works in order to adjust your settings - 
3. Setup your virtualenv python3
4. pip install all items in requirements.txt
5. Run setup.py. It will create tables, and populate trending coins from Livecoin, and all markets in

Happy cuan bro
