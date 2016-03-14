import urwid
import sys
import argparse
import json
import decimal
import quote_fetcher

symbols = ["^GDAXI", "^GSPC",  "AAPL", "TSLA", "T", "GOOGL", "TWTR", "GE", "MSFT", "BAC"]

data = {}
quote_rows = []

UPDATE_INTERVAL=5

class QuoteRow(urwid.WidgetWrap):

	def __init__(self, symbol, last_quote, last_quote_date_time, percent_change, exchange):
		self.text_fields = {
			"symbol": urwid.AttrMap(urwid.Text(symbol), 'quote_default'),
			"last_quote" : urwid.AttrMap(urwid.Text(last_quote), 'quote_default'),
			"last_quote_date_time":urwid.AttrMap(urwid.Text(last_quote_date_time), 'quote_default'),
			"percent_change" : urwid.AttrMap(urwid.Text(percent_change), 'quote_default'),
			"exchange":urwid.AttrMap(urwid.Text(exchange), 'quote_default')
		}
		self.urwid_columns = urwid.Columns([self.text_fields["symbol"],
							self.text_fields["last_quote"],
							self.text_fields["last_quote_date_time"],
							self.text_fields["percent_change"],
							self.text_fields["exchange"]])
		urwid.WidgetWrap.__init__(self, self.urwid_columns)

	def update_quote(self, new_quote, last_quote_date_time, percent_change, exchange):
		last = decimal.Decimal(self.text_fields["last_quote"].original_widget.get_text()[0])
		new = decimal.Decimal(new_quote)
		if new == last:
			self.text_fields["last_quote"].set_attr_map({None: 'quote_default'})
		elif new > last:
			self.text_fields["last_quote"].set_attr_map({None: 'quote_higher'})
		else:
			self.text_fields["last_quote"].set_attr_map({None: 'quote_lower'})
		self.text_fields["last_quote"].original_widget.set_text(new_quote)
		self.text_fields["last_quote_date_time"].original_widget.set_text(last_quote_date_time)
		self.text_fields["percent_change"].original_widget.set_text(percent_change)
	
	def get_symbol(self):
		return self.text_fields["symbol"].original_widget.get_text()[0]

def handle_input(input):
	if input == "esc":
		sys.exit(0)
	pass

def fetch_quotes(urwid_main_loop, user_data):
	quotes = quote_fetcher.get_quotes(symbols)
	for quote_row in quote_rows:
		for symbol, quote in quotes.iteritems():
			if quote_row[1].get_symbol() == symbol:
				quote_row[1].update_quote(quote["LastPrice"], 
							quote["LastTradeDateTime"],
							quote["ChangeInPercent"],
							quote["Exchange"])
	urwid_main_loop.draw_screen()
	urwid_main_loop.set_alarm_in(UPDATE_INTERVAL, fetch_quotes)

def main():
	parser = argparse.ArgumentParser(description="Show live quotes for Stocks/Indices/Currencies")
	parser.add_argument('symbols', metavar='stock-symbol', type=str, nargs='*', help='ticker symbols')
	args = parser.parse_args()
	global symbols, quote_rows
	if len(args.symbols) > 0:
		symbols = args.symbols
	quotes = quote_fetcher.get_quotes(symbols)
	quote_rows = [('pack', QuoteRow("Symbol", "LastPrice", "LastPriceDateTime", "Change %", "Exchange"))]
	for symbol, symbol_data in quotes.iteritems():
		quote_rows.append(('pack', QuoteRow(symbol, symbol_data["LastPrice"], 
				symbol_data["LastTradeDateTime"], symbol_data["ChangeInPercent"], symbol_data["Exchange"])))

	palette = [('quote_higher','dark green', 'black', 'standout'),
		   ('quote_lower', 'dark red', 'black', 'standout'),
		   ('quote_default', 'white', 'black', 'standout')]

	loop = urwid.MainLoop(urwid.Filler(urwid.Pile(quote_rows), 'top'), palette, unhandled_input=handle_input)
	loop.set_alarm_in(UPDATE_INTERVAL, fetch_quotes)
	loop.run()

if __name__ == '__main__':
	main()
