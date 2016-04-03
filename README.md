# stocktop
stocktop is a text-based user interface for monitoring stocks/indices/currencies intraday.
Currently stocktop uses myql (https://github.com/josuebrunel/myql) to get stock quotes from Yahoo via YQL (see https://developer.yahoo.com/yql/).

## Running stocktop
stocktop runs with Python 2.7.
Just run 
	make install
to install all needed dependencies (or install myql and urwid via pip directly).

Afterwards stocktop can be started with:

	python stocktop.py

## Screenshot
[[https://github.com/rthaenert/stocktop/blob/master/doc/screenshot.png|alt=screenshot]

## Commands
	+: Add a Ticker Symbol to the list
	-: Remove the current Ticker Symbol
 
