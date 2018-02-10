import context
import leg
from leg import Leg
import unittest
import datetime
# import handler
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import alchemy_utils
import numpy as np


class TestPersist(unittest.TestCase):

    @unittest.skip('Need to install local SQL DB.')
    def test_save_to_local(self): 
        for i in range(2):
            handler.scrape(1, 'LGW', 'DUB', datetime.datetime.now() + datetime.timedelta(days=7+i))

    @unittest.skip('Need to install local SQL DB.')
    def test_random_sample(self):
        session = handler.Session()
        l = session.query(Leg).all()
        b = np.array(l)
        pick = np.random.randint(len(b), size=6)
        for sample in b[pick]:
            print('\nDeparture date: {}\nPrice: {}\nFrom: {}\nTo: {}\nAirline: {}'.format(sample.departure_date, sample.price, sample.departure_location, sample.arrival_location, sample.airline))

    def test_persist_leg(self):
        leg = self._create_leg()
        #engine = create_engine('mysql+pymysql://root:password@localhost/jambalaya', echo=True)
        engine = create_engine('sqlite://', echo=True) # in memory sqlite DB
        alchemy_utils.Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        session.add(leg)
        session.commit()
        loaded_leg = session.query(Leg).first()
        self.assertEqual(leg, loaded_leg)

    def _create_leg(self):
        download_day = datetime.datetime(year=2017, month=12, day=26)
        return Leg(price=20.0, departure_location='DEP', arrival_location='ARR', departure_date=download_day + datetime.timedelta(days=10), request_time=download_day, duration=datetime.timedelta(hours=2), airline='Qantas')


if __name__ == '__main__':
    unittest.main()
