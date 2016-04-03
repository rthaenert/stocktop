import urwid
import os
import sys
import argparse
import json
import decimal
import logging
import threading

symbols = ["^GDAXI", "^GSPC",  "AAPL", "TSLA", "T", "GOOGL", "TWTR", "GE", "MSFT", "BAC", "DB1.DE", "DB", "CBK.DE", "GS"]

urwid_pile = None
scheduled_timer = None
UPDATE_INTERVAL=5
loop = None

logging.basicConfig(level=logging.DEBUG, filename='../stocktop.log')
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
		self.__super.__init__(urwid.AttrWrap(urwid.ListBox([symbol_label, symbol_input, ok_button, close_button]), 'popbg'))

class TickerSymbolPopUpLauncher(urwid.PopUpLauncher):
	def __init__(self):
		self.__super.__init__(urwid.Text(""))
		
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
		logger.debug(self.symbol.text)
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
		# TODO
		if scheduled_timer is not None:
			scheduled_timer.cancel()
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
	urwid_pile.contents.append((quote_row, ('pack', None)))
	symbols.append(symbol)

def fetch_quotes():
	quotes = quote_fetcher.get_quotes(symbols)
	update_quotes_ui(quotes)
	scheduled_timer = threading.Timer(UPDATE_INTERVAL, fetch_quotes)
	scheduled_timer.start()
	loop.draw_screen()

def update_quotes_ui(quotes):
	for row in urwid_pile.contents:
		quote_row = row[0]
		symbol = quote_row.get_symbol()
		if symbol in quotes:
			quote = quotes[symbol]
			quote_row.update_quote(**quote)
	


def main():
	parser = argparse.ArgumentParser(description="Show live quotes for Stocks/Indices/Currencies")
	parser.add_argument('symbols', metavar='stock-symbol', type=str, nargs='*', help='ticker symbols')
	args = parser.parse_args()
	global symbols, urwid_pile, popup_launcher, scheduled_timer, loop
	if len(args.symbols) > 0:
		symbols = args.symbols

	quotes = quote_fetcher.get_quotes(symbols)
	quote_rows = [('pack', QuoteRow("Symbol", "LastPrice", "LastPriceDateTime", "Change %", "Exchange"))]
	for symbol, symbol_data in quotes.iteritems():
		quote_rows.append(('pack', QuoteRow(symbol, symbol_data["LastPrice"], 
				symbol_data["LastTradeDateTime"], symbol_data["ChangeInPercent"], symbol_data["Exchange"])))

	palette = [('header', 'white,underline', 'black', 'standout, underline'),
		   ('quote_higher','white', 'dark green', 'standout, bold'),
		   ('quote_lower', 'white', 'dark red', 'standout, bold'),
		   ('quote_default', 'white', 'black', 'standout'),
		   ('popbg', 'white', 'dark blue')]
	urwid_pile = urwid.Pile(quote_rows)
	popup_launcher = TickerSymbolPopUpLauncher()	
	footer_text = urwid.Text("+: Add Symbol -: Remove Symbol Esc: Quit")
	loop = urwid.MainLoop(urwid.Frame(header=urwid.AttrWrap(urwid.Text("Stocktop"), 'header'),
					body=(urwid.Filler(urwid_pile, 'top')), 
					footer=urwid.Columns([popup_launcher, footer_text])),
					palette, unhandled_input=handle_input, pop_ups=True)
	scheduled_timer = threading.Timer(UPDATE_INTERVAL, fetch_quotes)
	scheduled_timer.start()
	loop.watch_pipe(update_quotes_ui)
	loop.run()

if __name__ == '__main__':
	main()
