import context
import downloader
import scrape_parser
import unittest
import datetime
import pickle as pkl
from pathlib import Path
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot
import matplotlib.dates

class TestDownloadAndParse(unittest.TestCase):
    
    path = '../data/boxing_day_scrapes.pkl'
    boxing_day = datetime.date(year=2017, month=12, day=26)

    @classmethod
    def setUpClass(cls):
        '''
        Download all the scrapes from boxing day and dump them in cls.path, if this hasn't been done already.
        If you change downloader it's a good idea to delete the stuff in cls.path so this starts from scratch.
        This is a bit rubbish but downloading everything takes a while.
        '''
        if not Path(cls.path).is_file():
            downloader.download_all_on_day(cls.boxing_day, file=cls.path)

    def unpickle_file(self, path):
        with open(path, 'rb') as f:
            unpickled = pkl.load(f)
        return unpickled

    
    def test_get_same_flight(self):
        unpickled = self.unpickle_file(self.path)
        all_legs = []

        for scrape in unpickled:
            for leg in filter(lambda l: l['stops'] == 0, scrape[1].values()):
                nums = scrape_parser.Leg(self.boxing_day, leg)
                all_legs.append(nums)

        # todo use itertools#groupby to do this properly
        first = all_legs[0]
        same_as_first = []
        for num in all_legs:
            if num.represents_same_leg(first):
                same_as_first.append(num)

        self.assertEqual(19, len(same_as_first), 'Should have this flight for each of the 19 scrapes')

        request_order = sorted(same_as_first, key=lambda l: l.request_time)

        datetimes = [leg.request_time for leg in request_order]
        prices = [leg.price for leg in request_order]
        dates = matplotlib.dates.date2num(datetimes)
        matplotlib.pyplot.plot_date(dates, prices)
        # matplotlib.pyplot.show()

if __name__ == '__main__':
    unittest.main()
