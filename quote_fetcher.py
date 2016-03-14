import yahoo_finance
import time
import urllib2

yahoo_time_format = "%Y-%m-%d %H:%M:%S %Z"

def parse_datetime(date_time_str):
	last_trade_date_time, offset_str = date_time_str[:-5], date_time_str[-5:]
	# TODO handle UTC offset correctly, currently its left out
	return time.strptime(last_trade_date_time, yahoo_time_format)

def update_quote_yahoo(quotes_dict, symbol):
	quote = yahoo_finance.Share(symbol)
	quotes_dict[symbol] = {
		"Exchange" : quote.get_stock_exchange(),
		"LastPrice": quote.get_price().replace(',',''),
		"LastTradeDateTime": quote.get_trade_datetime(),
		"ChangeInPercent": quote.get_change_in_percent(),
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
	map(lambda symbol: update_quote_yahoo(quotes_merged, symbol), symbols)
	return quotes_merged

if __name__ == "__main__":
	import pprint
	print pprint.pprint(get_quotes(["^GDAXI"]))
