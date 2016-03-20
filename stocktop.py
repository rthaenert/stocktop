import urwid
import sys
import argparse
import json
import decimal
import quote_fetcher

symbols = ["^GDAXI", "^GSPC",  "AAPL", "TSLA", "T", "GOOGL", "TWTR", "GE", "MSFT", "BAC"]
quote_rows = []
urwid_pile = None
UPDATE_INTERVAL=5

class AddTickerSymbolDialog(urwid.WidgetWrap):
	def __init__(self):
		close_button = urwid.Button("Close")

class TickerSymbol(urwid.SelectableIcon):
	
	def keypress(self, size, key):
		if key == '-':
			remove_quote_from_ui(self.text)
		elif key == '+':
			AddQuoteDialog()
		return key

class QuoteRow(urwid.WidgetWrap):

	def __init__(self, symbol, last_quote, last_quote_date_time, percent_change, exchange):
		self.symbol = TickerSymbol(symbol, 0)
		self.text_fields = {
			"LastPrice" : urwid.AttrMap(urwid.Text(last_quote), 'quote_default'),
			"LastTradeDateTime":urwid.AttrMap(urwid.Text(last_quote_date_time), 'quote_default'),
			"ChangeInPercent" : urwid.AttrMap(urwid.Text(percent_change), 'quote_default'),
			"Exchange":urwid.AttrMap(urwid.Text(exchange), 'quote_default')
		}
		self.urwid_columns = urwid.Columns([self.symbol,
							self.text_fields["LastPrice"],
							self.text_fields["LastTradeDateTime"],
							self.text_fields["ChangeInPercent"],
							self.text_fields["Exchange"]])
		urwid.WidgetWrap.__init__(self, self.urwid_columns)

	def update_quote(self, **kwargs):
		last_price_field = self.text_fields["LastPrice"]
		
		last = decimal.Decimal(last_price_field.original_widget.get_text()[0])
		new = decimal.Decimal(kwargs["LastPrice"])
		if new == last:
			last_price_field.set_attr_map({None: 'quote_default'})
		elif new > last:
			last_price_field.set_attr_map({None: 'quote_higher'})
		else:
			last_price_field.set_attr_map({None: 'quote_lower'})

		for key in kwargs:
			if key in self.text_fields:
				self.text_fields[key].original_widget.set_text(kwargs[key])
	
	def get_symbol(self):
		return self.symbol.text
	
def handle_input(input):
	if input == "esc":
		sys.exit(0)
	pass

def remove_quote_from_ui(symbol):
	for row in urwid_pile.contents:
		if row[0].get_symbol() == symbol:
			urwid_pile.contents.remove(row)

def fetch_quotes(urwid_main_loop, user_data):
	quotes = quote_fetcher.get_quotes(symbols)
	for quote_row in quote_rows:
		symbol = quote_row[1].get_symbol()
		if symbol in quotes:
			quote = quotes[symbol]
			quote_row[1].update_quote(**quote)
	urwid_main_loop.draw_screen()
	urwid_main_loop.set_alarm_in(UPDATE_INTERVAL, fetch_quotes)

def main():
	parser = argparse.ArgumentParser(description="Show live quotes for Stocks/Indices/Currencies")
	parser.add_argument('symbols', metavar='stock-symbol', type=str, nargs='*', help='ticker symbols')
	args = parser.parse_args()
	global symbols, quote_rows, urwid_pile
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
	urwid_pile = urwid.Pile(quote_rows)
	loop = urwid.MainLoop(urwid.Filler(urwid_pile, 'top'), palette, unhandled_input=handle_input)
	loop.set_alarm_in(UPDATE_INTERVAL, fetch_quotes)
	loop.run()

if __name__ == '__main__':
	main()
