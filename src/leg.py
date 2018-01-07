from datetime import datetime
from datetime import timedelta
import dateutil.parser
from typing import List
import alchemy_utils
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Sequence, Float, DateTime, Interval, ForeignKey


class CarrierCode(alchemy_utils.Base):
    __tablename__ = 'carrier_code'
    leg_id = Column(Integer, ForeignKey('leg.id'), primary_key=True)
    order = Column(Integer, primary_key=True) # 0-indexed position in the Leg's list of carrier codes
    carrier_code = Column(String(2), primary_key=True) # IATA airline code

    def make_tuple(self):
        return (self.leg_id, self.order, self.carrier_code)


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
    carrier_codes = relationship("CarrierCode", order_by=CarrierCode.order)


    def _contain_same_codes(self, other_codes):
        this = {code.make_tuple() for code in self.carrier_codes}
        other = {other.make_tuple() for other in other_codes}
        return this == other


    def represents_same_leg(self, other):
        """
        Returns true if this object represents the same flight as other
        """
        return self.departure_location == other.departure_location and\
        self._contain_same_codes(other.carrier_codes) and\
        self.arrival_location == other.arrival_location and\
        self.departure_date == other.departure_date


    def __repr__(self):
        return str(self.__dict__)


def create_leg(request_time: datetime, leg_json: dict) -> Leg:
    price = float(leg_json['price']['totalPriceAsDecimal']) #: Its price when we enquired
    n_stops = int(leg_json['stops'])  #: How many stopovers there are on the journey

    departure_location = leg_json['departureLocation']['airportCode']  #: Where the plane leaves from eg 'LGW'
    arrival_location = leg_json['arrivalLocation']['airportCode']  #: Where the plane lands eg 'MAD'

    d = leg_json['departureTime']['isoStr']
    departure_date = dateutil.parser.parse(d)  #: When the flight takes off
 
    duration = leg_json['duration']
    duration = timedelta(hours=duration['hours'], minutes=duration['minutes'])  #: How long the flight takes
 
    carriers = leg_json['carrierSummary']['airlineCodes']
    leg = Leg(price=price, n_stops=n_stops, departure_location=departure_location, arrival_location=arrival_location,\
        departure_date=departure_date, duration=duration, request_time=request_time)
    leg.carrier_codes = [CarrierCode(order=i, carrier_code=carriers[i]) for i in range(len(carriers))]
    return leg
