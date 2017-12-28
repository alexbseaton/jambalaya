from context import downloader
import unittest
import datetime

class TestScrape(unittest.TestCase):
    def test_scrape(self):
        self.assertEqual(19, len(downloader.download_all_on_day(datetime.date(year=2017, month=12, day=26))))

if __name__ == '__main__':
    unittest.main()
