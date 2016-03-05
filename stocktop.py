import urwid
import sys
import argparse
import googlefinance
import json
import tabulate

def handle_input(input):
	if input == "esc":
		sys.exit(0)
	pass

def update_quotes(stock_symbols):
	quotes = googlefinance.getQuotes(stock_symbols)
	# TODO there is a pythonic way for this!
	headers = ["Symbol", "LastTradeDateTime", "LastTradePrice"]
	new_quotes = []
	for quote in quotes:
		new_quotes.append([quote["StockSymbol"], quote["LastTradeDateTime"], quote["LastTradePrice"]])
	return tabulate.tabulate(new_quotes, headers=headers)

def main():
	parser = argparse.ArgumentParser(description="Process some ISINs/WKNs")
	parser.add_argument('symbols', metavar='stock-symbol', type=str, nargs='+', help='a ticker symbol')
	args = parser.parse_args()
	text = urwid.Text(update_quotes(args.symbols))
	text = urwid.Filler(text, 'top')
	loop = urwid.MainLoop(text,unhandled_input=handle_input)
	loop.run()

if __name__ == '__main__':
	main()
