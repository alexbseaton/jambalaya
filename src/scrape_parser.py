from datetime import datetime
from datetime import timedelta
import dateutil.parser
from typing import List
import alchemy_utils
from sqlalchemy import Column, Integer, String, Sequence, Float, DateTime, Interval


class Leg(alchemy_utils.Base):
    """
    Takes a leg from the Expedia JSON and returns a more manageable object holding
    a subset of its data.

    Args:
        time: the timestamp for when the leg was saved. In %d-%m-%y_%H_%M format.
        leg: a dict representing a 'leg' from the Expedia JSON file
    Returns:
        A leg object containing a subset of the data from the JSON file
    """
    __tablename__ = 'leg'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    price = Column(Float())
    n_stops = Column(Integer())
    departure_location = Column(String(3))
    arrival_location = Column(String(3))
    departure_date = Column(DateTime())
    request_time = Column(DateTime())
    duration = Column(Interval())


    def represents_same_leg(self, other):
        """
        Returns true if this object represents the same flight as other
        """
        # TODO self.carriers == other.carriers and
        return self.departure_location == other.departure_location and\
        self.arrival_location == other.arrival_location and\
        self.departure_date == other.departure_date


    def __repr__(self):
        return str(self.__dict__)


def create_leg(request_time: datetime, leg: dict) -> Leg:
    price = float(leg['price']['totalPriceAsDecimal']) #: Its price when we enquired
    n_stops = int(leg['stops'])  #: How many stopovers there are on the journey

    departure_location = leg['departureLocation']['airportCode']  #: Where the plane leaves from eg 'LGW'
    arrival_location = leg['arrivalLocation']['airportCode']  #: Where the plane lands eg 'MAD'

    d = leg['departureTime']['isoStr']
    departure_date = dateutil.parser.parse(d)  #: When the flight takes off
 
    duration = leg['duration']
    duration = timedelta(hours=duration['hours'], minutes=duration['minutes'])  #: How long the flight takes
 
    request_time = request_time  #: When we enquired about the flight

    # Want a join table to this chappy
    # Always a list, in case there are multiple stops
    carriers = leg['carrierSummary']['airlineCodes']  #: https://en.wikipedia.org/wiki/List_of_airline_codes
    # TODO need to figure out how to do carriers
    return Leg(price=price, n_stops=n_stops, departure_location=departure_location, arrival_location=arrival_location,\
        departure_date=departure_date, duration=duration, request_time=request_time)
