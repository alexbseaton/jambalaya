import context
import downloader
import leg
from leg import Leg
import unittest
import datetime
import pickle as pkl
from pathlib import Path
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot
import matplotlib.dates
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import alchemy_utils
import test_utils


class TestDownloadAndParse(unittest.TestCase):

    download_day = datetime.date(year=2017, month=12, day=26)

    def setUp(self):
        jsons = [test_utils.create_mock_leg_json(100.0, 2, 'LGW', 'MAD', datetime.datetime(2017, 2, 1), 2, 30, ['AB', 'CD']),\
        test_utils.create_mock_leg_json(200.0, 2, 'LGW', 'MAD', datetime.datetime(2017, 2, 1), 2, 32, ['AB', 'CD']), # same flight\
        test_utils.create_mock_leg_json(210.0, 2, 'LGW', 'MAD', datetime.datetime(2017, 2, 1), 2, 28, ['AB', 'CD']), # same flight\
        test_utils.create_mock_leg_json(200.0, 2, 'LGW', 'GVA', datetime.datetime(2017, 2, 1), 2, 30, ['AB', 'CD']), # different arrival\
        test_utils.create_mock_leg_json(200.0, 2, 'LHR', 'MAD', datetime.datetime(2017, 2, 1), 2, 30, ['AB', 'CD']), # different departure\
        test_utils.create_mock_leg_json(200.0, 2, 'LGW', 'MAD', datetime.datetime(2017, 2, 1), 2, 32, ['AB', 'EF']), # different carriers\
        test_utils.create_mock_leg_json(100.0, 2, 'LGW', 'MAD', datetime.datetime(2017, 2, 2), 2, 30, ['AB', 'CD'])] # different departure date
        self.all_legs = [leg.create_leg(self.download_day + datetime.timedelta(days=i), jsons[i]) for i in range(len(jsons))]


    def test_get_same_flight(self):
        first = self.all_legs[0]
        same_as_first = [l for l in self.all_legs if l.represents_same_leg(first)]
        self.assertEqual(3, len(same_as_first), 'Should have this flight for the first three things in jsons')


    def test_persist_leg(self):
        first = self.all_legs[0]
        #engine = create_engine('mysql+pymysql://root:password@localhost/jambalaya', echo=True)
        engine = create_engine('sqlite://', echo=True) # in memory sqlite DB
        alchemy_utils.Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        session.add(first)
        session.commit()
        loaded_leg = session.query(Leg).first()
        self.assertEqual(first, loaded_leg)


if __name__ == '__main__':
    unittest.main()
