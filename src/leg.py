from datetime import datetime
from datetime import timedelta
import dateutil.parser
from typing import List
import alchemy_utils
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Sequence, Float, DateTime, Interval, ForeignKey, DECIMAL


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
    price = Column(DECIMAL(15,2))
    departure_location = Column(String(3))
    arrival_location = Column(String(3))
    departure_date = Column(DateTime())
    request_time = Column(DateTime())
    duration = Column(Interval())
    airline = Column(String(100))


    def represents_same_leg(self, other):
        """
        Returns true if this object represents the same flight as other
        """
        return self.departure_location == other.departure_location and\
        self.airline == other.airline and\
        self.arrival_location == other.arrival_location and\
        self.departure_date == other.departure_date


    def similar_flights(self, all_legs):
        """
        Those legs representing the same flight as this one, just with data
        gathered at a different time.

        Args:
            all_legs: An iterable of Leg objects to compare to this one
        Returns:
            A list of the legs in all_legs that are similar to this one
        """
        return [f for f in all_legs if f.represents_same_leg(self)]


    def __repr__(self):
        return str(self.__dict__)


def make_groups(legs):
    """
    Gives a list of lists of legs that all represent the same flight.
    See the similar_flights method of Leg.

    Args:
        legs: the legs to group into lists that are the same flight
    Returns:
        A list of lists of Leg objects where all the elements in each sub-list
        represent the same flight.
    """
    grouped = []
    matched = {leg:False for leg in legs}
    for leg in l:
        if matched[leg]:
            continue
        sim = leg.similar_flights(legs)
        grouped.append(sim)
        for s in sim:
            matched[s] = True

    return grouped