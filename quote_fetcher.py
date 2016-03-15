import myql
import time
import json
import logging

yahoo_time_format = "%Y-%m-%d %H:%M:%S %Z"

yql = myql.MYQL(community=True)

# disable logging as this breaks the urwid display
logging.getLogger('mYQL').setLevel(logging.ERROR)
logging.getLogger('requests').setLevel(logging.ERROR)

def parse_datetime(date_time_str):
	last_trade_date_time, offset_str = date_time_str[:-5], date_time_str[-5:]
	# TODO handle UTC offset correctly, currently its left out
	return time.strptime(last_trade_date_time, yahoo_time_format)

def _update_quote(quote, quotes_merged):
	quotes_merged[quote["Symbol"]] = {"Exchange": quote["StockExchange"],
					"LastPrice": quote["LastTradePriceOnly"].replace(',',''),
					"LastTradeDateTime": quote["LastTradeDate"] + " " + quote["LastTradeTime"],
					"ChangeInPercent": quote["ChangeinPercent"] }

def get_quotes(symbols):
	if isinstance(symbols, str):
		symbols = [ symbols ]
	if not isinstance(symbols, list):
		return {}
	quotes_merged = {symbol : {
		"LastPrice" : "",
		"LastTradeDateTime" : "",
		"ChangeInPercent": "",
		"Exchange": ""} for symbol in symbols}	
	response = yql.select('yahoo.finance.quotes', 
			['Symbol', 'LastTradeDate', 'LastTradeTime', 'LastTradePriceOnly', 'ChangeinPercent', 'StockExchange']).where(['symbol', 'IN', symbols])
	if response.status_code != 200:
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
	print get_quotes(["AAPL"])
