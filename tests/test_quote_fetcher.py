import unittest
import requests
from ..stocktop import quote_fetcher

class YQLMock():
	def select(self, table, columns):
		return self

	def where(self, conditions):
		raise requests.exceptions.ConnectionError()

class TestQuoteFetcher(unittest.TestCase):
	def test_no_network_access_returns_without_exception(self):
		quote_fetcher.get_quotes(["AAPL"], YQLMock())
		self.assertTrue(True, "quote fetcher should not throw exceptions")

if __name__ == '__main__':
	unittest.main()
