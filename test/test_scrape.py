import context
import handler
import unittest

class TestScrape(unittest.TestCase):
    def test_scrape_parser(self):
        print(handler.scrape(5, 'alex-jambalaya-json-dumps', 'LGW', 'MAD', '1/17/2018'))

    def test_handler(self):
        handler.my_handler(None, None)

if __name__ == '__main__':
    unittest.main()
