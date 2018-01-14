import context
import leg
from leg import Leg
import unittest
import datetime
import handler
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import alchemy_utils


class TestPersist(unittest.TestCase):

    def test_save_to_local(self):
        handler.scrape(5, 'LGW', 'MAD', datetime.datetime.now() + datetime.timedelta(days=7))

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
