from context import handler
import unittest

class TestScrape(unittest.TestCase):
    def test_scrape(self):
        print(handler.scrape(5, 'alex-jambalaya-json-dumps'))

if __name__ == '__main__':
    unittest.main()
