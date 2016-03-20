import urwid
import sys
import argparse
import json
import decimal
import logging

symbols = ["^GDAXI", "^GSPC",  "AAPL", "TSLA", "T", "GOOGL", "TWTR", "GE", "MSFT", "BAC"]

quote_rows = []
urwid_pile = None
UPDATE_INTERVAL=5


logging.basicConfig(level=logging.DEBUG, filename='stocktop.log')
logger = logging.getLogger('stocktop')

import quote_fetcher

class AddTickerSymbolDialog(urwid.WidgetWrap):
	signals = ['close', 'add']

	def __init__(self):
		symbol_label = urwid.Text("Ticker Symbol")
		symbol_input = urwid.Edit("")
		ok_button = urwid.Button("Add")
		close_button = urwid.Button("Cancel")
		urwid.connect_signal(close_button, 'click', lambda button:self._emit('close'))
		urwid.connect_signal(ok_button, 'click', lambda button:self._emit('add', symbol_input.get_text()))
		self.__super.__init__(urwid.ListBox([symbol_label, symbol_input, ok_button, close_button]))

class TickerSymbolPopUpLauncher(urwid.PopUpLauncher):
	def __init__(self):
		self.__super.__init__(urwid.Text("+: Add Symbol"))
		
	def create_pop_up(self):
		pop_up = AddTickerSymbolDialog()
		urwid.connect_signal(pop_up, 'close', lambda button:self.close_pop_up())
		urwid.connect_signal(pop_up, 'add', self.add_symbol_and_close)
		return pop_up

	def add_symbol_and_close(self, button, symbol):
		add_symbol_to_ui(button, symbol)
		self.close_pop_up()

	def get_pop_up_parameters(self):
		return {'left':10, 'top':10, 'overlay_width':32, 'overlay_height':7}

class TickerSymbol(urwid.SelectableIcon):
	def __init__(self, text, cursor_position=0):
		super(TickerSymbol, self).__init__(text, cursor_position)
		self.pop_up_launcher = TickerSymbolPopUpLauncher()
	
	def keypress(self, size, key):
		if key == '-':
			remove_symbol_from_ui(self.text)
		elif key == '+':
			popup_launcher.open_pop_up()
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
		last_price = last_price_field.original_widget.get_text()[0]	
		last = decimal.Decimal(last_price) if last_price is not '' else decimal.Decimal(0)
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

def remove_symbol_from_ui(symbol):
	for row in urwid_pile.contents:
		if row[0].get_symbol() == symbol:
			urwid_pile.contents.remove(row)

def add_symbol_to_ui(button, symbol):
	symbol = symbol[0]
	for row in urwid_pile.contents:
		if row[0].get_symbol() == symbol:
			logger.debug("Symbol {} already in List. skipping.".format(symbol))
			return
	
	logger.debug("Contents: {}".format(urwid_pile.contents))
	quote_row = QuoteRow(symbol, "","","","")
	# FIXME should be enough to only store the Pile globally
	quote_rows.append(('pack', quote_row))
	urwid_pile.contents.append((quote_row, ('pack', None)))
	symbols.append(symbol)

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
	global symbols, quote_rows, urwid_pile, popup_launcher
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
	popup_launcher = TickerSymbolPopUpLauncher()	
	loop = urwid.MainLoop(urwid.Frame(header=urwid.Text("Stocktop"), 
					body=(urwid.Filler(urwid_pile, 'top')), 
					footer=popup_launcher),
					palette, unhandled_input=handle_input, pop_ups=True)
	loop.set_alarm_in(UPDATE_INTERVAL, fetch_quotes)
	loop.run()

if __name__ == '__main__':
	main()
