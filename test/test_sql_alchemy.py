import context
import handler
import scrape_parser
from scrape_parser import Leg
import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
import alchemy_utils


class TestAlchemy(unittest.TestCase):
    def test(self):
        #engine = create_engine('mysql+pymysql://root:password@localhost/jambalaya', echo=True)
        engine = create_engine('sqlite://', echo=True) # in memory sqlite DB

        print(alchemy_utils.Base.metadata.create_all(engine))
        Session = sessionmaker(bind=engine)
        request_time = datetime.datetime(2018, 1, 2, 12, 16, 0)
        price = 127.32
        n_stops = 2
        departure_location = 'LGW'
        arrival_location = 'MAD'
        departure_date = datetime.datetime(2018, 2, 2, 12, 16, 0)
        duration = datetime.timedelta(hours=2, minutes=15)
        leg = Leg(request_time=request_time, price=price, n_stops=n_stops, departure_location=departure_location\
        ,arrival_location=arrival_location, departure_date=departure_date, duration=duration)

        session = Session()
        session.add(leg)

        our_leg = session.query(Leg).filter_by(request_time=request_time).first()
        print(our_leg)

        session.commit()


if __name__ == '__main__':
    unittest.main()
