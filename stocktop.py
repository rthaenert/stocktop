import urwid
import sys
import argparse
import googlefinance
import json
import decimal

stock_symbols = ["AAPL", "TSLA", "T", "GOOGL", "TWTR"]
data = {}
quote_rows = []

class QuoteRow(urwid.WidgetWrap):
	def __init__(self, symbol, last_quote):
		self.symbol_text = urwid.AttrMap(urwid.Text(symbol), 'quote_default')
		self.last_quote_text = urwid.AttrMap(urwid.Text(last_quote), 'quote_default')
		self.urwid_columns = urwid.Columns([self.symbol_text, self.last_quote_text])
		urwid.WidgetWrap.__init__(self, self.urwid_columns)

	def update_quote(self, new_quote):
		last = decimal.Decimal(self.last_quote_text.original_widget.get_text()[0])
		new = decimal.Decimal(new_quote)
		if new == last:
			self.last_quote_text.set_attr_map({None: 'quote_default'})
		elif new > last:
			self.last_quote_text.set_attr_map({None: 'quote_higher'})
		else:
			self.last_quote_text.set_attr_map({None: 'quote_lower'})
		self.last_quote_text.original_widget.set_text(new_quote)
	
	def get_symbol(self):
		return self.symbol_text.original_widget.get_text()[0]

def handle_input(input):
	if input == "esc":
		sys.exit(0)
	pass

def update_quotes(stock_symbols):
	quotes = googlefinance.getQuotes(stock_symbols)
	for quote in quotes:
		data[ quote["StockSymbol"] ] = quote["LastTradePrice"] 
	return data

def test_callback(urwid_main_loop, user_data):
	quotes = update_quotes(stock_symbols)
	# TODO improve this
	for quote_row in quote_rows:
		for symbol, quote in quotes.iteritems():
			if quote_row[1].get_symbol() == symbol:
				quote_row[1].update_quote(quote)
	urwid_main_loop.draw_screen()
	urwid_main_loop.set_alarm_in(5, test_callback)

def main():
	parser = argparse.ArgumentParser(description="Show live stocks")
	parser.add_argument('symbols', metavar='stock-symbol', type=str, nargs='*', help='a ticker symbol')
	args = parser.parse_args()
	global stock_symbols, quote_rows
	if len(args.symbols) > 0:
		stock_symbols = args.symbols
	quotes = update_quotes(stock_symbols)
	quote_rows = []
	for symbol, quote in quotes.iteritems():
		quote_rows.append(('pack', QuoteRow(symbol, quote)))

	palette = [('quote_higher','dark green', 'black', 'standout'),
		   ('quote_lower', 'dark red', 'black', 'standout'),
		   ('quote_default', 'white', 'black', 'standout')]

	loop = urwid.MainLoop(urwid.Filler(urwid.Pile(quote_rows)), palette, unhandled_input=handle_input)
	loop.set_alarm_in(5, test_callback)
	loop.run()

if __name__ == '__main__':
	main()
