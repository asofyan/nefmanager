import configparser
from coinmarketcapapi import CoinMarketCapAPI, CoinMarketCapAPIError
config = configparser.RawConfigParser()
config.read('config.cfg')

cmc =  CoinMarketCapAPI(config['nefmanager']['cmc_api_key'])

curs = cmc.cryptocurrency_listings_latest(
	volume_24h_min=50000,
	volume_24h_max=100000,
	limit = 50,
	sort = 'volume_7d',
	sort_dir = 'desc',
	cryptocurrency_type = 'coins'
)
# why I got useless coins :-(
for c in curs.data:
	print(c['symbol'],'{:,}'.format(c['quote']['USD']['volume_24h']))