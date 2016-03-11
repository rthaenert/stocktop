import googlefinance
import yahoo_finance
import time
import urllib2

yahoo_time_format = "%Y-%m-%d %H:%M:%S %Z"
google_time_format = "%Y-%m-%dT%H:%M%SZ"

def parse_datetime(date_time_str, source):
	yahoo_datetime = time.strptime(last_trade_date_time, yahoo_time_format)
	google_lasttime = quotes_merged[symbol]["LastTradeDateTime"]
	if source == "google":
		return time.strptime(date_time_str, google_time_format)
	else:	# currently only yahoo
		last_trade_date_time, offset_str = yahoo_datetime[:-5], yahoo_datetime[-5:]
		# TODO handle UTC offset correctly, currently its left out
		return time.strptime(last_trade_date_time, yahoo_time_format)

def update_quote_google(quotes_dict, new_quote):
	symbol = new_quote["StockSymbol"]
	if not quotes_dict[symbol] or quotes_dict[symbol]["LastTradeDateTime"] == "":
		quotes_dict[symbol] = {
			"Exchange" : new_quote["Index"],
			"LastPrice": new_quote["LastTradePrice"].replace(',',''),
			"LastTradeDateTime": new_quote["LastTradeDateTime"],
			"ChangeInPercent": new_quote["ChangePercent"],
			"Source": "google"
		}
	else: 
		pass
	return quotes_dict	

def update_quote_yahoo(quotes_dict, symbol):
	if not quotes_dict[symbol] or quotes_dict[symbol]["LastTradeDateTime"]=="":
		# look up quote
		quote = yahoo_finance.Share(symbol)
		quotes_dict[symbol] = {
			"Exchange" : quote.get_stock_exchange(),
			"LastPrice": quote.get_price().replace(',',''),
			"LastTradeDateTime": quote.get_trade_datetime(),
			"ChangeInPercent": quote.get_change(),
			"Source" : "yahoo"
		}
	return quotes_dict	

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
	try:
		quotes_google = googlefinance.getQuotes(symbols)
		map(lambda new_quote : update_quote_google(quotes_merged, new_quote), quotes_google)
	except urllib2.HTTPError as e:
		# TODO log this error
		pass
	map(lambda symbol: update_quote_yahoo(quotes_merged, symbol), symbols)
	return quotes_merged

if __name__ == "__main__":
	import pprint
	print pprint.pprint(get_quotes(["^GDAXI"]))
