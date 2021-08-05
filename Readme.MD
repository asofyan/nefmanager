**NEF Manager**
by: asofyan@gmail.com

Python app to manage your trades by using Nefertiti Bot from command line.

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
2. Adjust your settings. You must understand how Nefertiti works in order to adjust your settings - https://nefertiti-tradebot.com/
3. Setup your virtualenv python3
4. pip install all items in requirements.txt
5. Run setup.py. It will create tables, and populate trending coins from Livecoin, and all markets in

Happy cuan bro