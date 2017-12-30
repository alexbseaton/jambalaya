from datetime import datetime
from datetime import timedelta
import dateutil.parser
from enum import Enum, unique
from typing import List


@unique
class TimeOfDay(Enum):
    morning = 'MORNING'
    afternoon = 'AFTERNOON'
    evening = 'EVENING'


class Leg(object):
    """
    Takes a leg from the Expedia JSON and returns a more manageable object holding
    a subset of its data.

    Args:
        time: the timestamp for when the leg was saved. In %d-%m-%y_%H_%M format.
        leg: a dict representing a 'leg' from the Expedia JSON file
    Returns:
        A leg object containing a subset of the data from the JSON file
    """

    def __init__(self, request_time: datetime, leg: dict):
        self.price = float(leg['price']['totalPriceAsDecimal']) #: Its price when we enquired
        self.n_stops = int(leg['stops'])  #: How many stopovers there are on the journey
        # Always a list, in case there are multiple stops
        self.carriers = leg['carrierSummary']['airlineCodes']  #: https://en.wikipedia.org/wiki/List_of_airline_codes
        self.departure_location = leg['departureLocation']['airportCode']  #: Where the plane leaves from eg 'LGW'
        self.arrival_location = leg['arrivalLocation']['airportCode']  #: Where the plane lands eg 'MAD'

        d = leg['departureTime']['isoStr']
        self.departure_date = dateutil.parser.parse(d)  #: When the flight takes off

        duration = leg['duration']
        self.duration = timedelta(hours=duration['hours'], minutes=duration['minutes'])  #: How long the flight takes

        self.departure_time_of_day = TimeOfDay(duration['departureTimeOfDay'])  #: When the flight leaves
        self.arrival_time_of_day = TimeOfDay(duration['arrivalTimeOfDay']) #: When the flights arrives

        self.request_time = request_time  #: When we enquired about the flight


    def represents_same_leg(self, other):
        """
        Returns true if this object represents the same flight as other
        """
        return self.carriers == other.carriers and\
        self.departure_location == other.departure_location and\
        self.arrival_location == other.arrival_location and\
        self.departure_date == other.departure_date

    def __repr__(self):
        return str(self.__dict__)
