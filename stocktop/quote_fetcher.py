import myql
import time
import json
import logging
import requests

yahoo_time_format = "%Y-%m-%d %H:%M:%S %Z"

yql = myql.MYQL(community=True)

# disable logging as this breaks the urwid display
logging.getLogger('mYQL').setLevel(logging.ERROR)
logging.getLogger('requests').setLevel(logging.ERROR)

logger = logging.getLogger('stocktop')

def parse_datetime(date_time_str):
	last_trade_date_time, offset_str = date_time_str[:-5], date_time_str[-5:]
	# TODO handle UTC offset correctly, currently its left out
	return time.strptime(last_trade_date_time, yahoo_time_format)

def _update_quote(quote, quotes_merged):
	quotes_merged[quote["Symbol"]] = {"Exchange": quote["StockExchange"],
					"LastPrice": quote["LastTradePriceOnly"].replace(',','') \
							if quote["LastTradePriceOnly"] is not None else "",
					"LastTradeDateTime": quote["LastTradeDate"] + " " + quote["LastTradeTime"] \
							if quote["LastTradePriceOnly"] is not None else "",
					"ChangeInPercent": quote["ChangeinPercent"] }

def get_quotes(symbols, yql=yql):
	""" Returns a dictionary of stock data for the given symbol(s).
	Example:
	{
		"LastPrice": "9200.39",
		"LastTradeDateTime": "",
		"ChangeInPercent" : "",
		"Exchange": "GER"
	}
	"""
	if isinstance(symbols, str):
		symbols = [ symbols ]
	if not isinstance(symbols, list):
		return {}
	quotes_merged = {symbol : {
		"LastPrice" : "",
		"LastTradeDateTime" : "",
		"ChangeInPercent": "",
		"Exchange": ""} for symbol in symbols}	
	try:
		response = yql.select('yahoo.finance.quotes', 
				['Symbol', 'LastTradeDate', 'LastTradeTime', 'LastTradePriceOnly', 'ChangeinPercent', 'StockExchange']).where(['symbol', 'IN', symbols])
	except requests.exceptions.ConnectionError as e:
		logger.error("Could not connect to Yahoo: " + str(e))
		return {}
	if response.status_code != 200:
		# TODO use a logger
		print "error getting quotes from yahoo"
		return quotes_merged
	response = response.json()["query"]["results"]
	if isinstance(response["quote"], dict):
		_update_quote(response["quote"], quotes_merged)
	elif isinstance(response["quote"], list):
		for quote in response["quote"]:
			_update_quote(quote, quotes_merged)
	return quotes_merged

if __name__ == "__main__":
	print get_quotes(["TSLA"])
