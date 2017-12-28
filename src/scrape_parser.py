import downloader
import pprint
import pickle as pkl
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
    """ Summary of information about a particular flight, in the state when it was requested.

    """

    def __init__(self, request_time: datetime, price: float, n_stops: int, carriers: List[str], 
    departure_location: str, arrival_location: str, departure_date: datetime,
    duration: timedelta, departure_time_of_day: TimeOfDay, arrival_time_of_day: TimeOfDay):
        self.request_time = request_time #: When we enquired about the flight
        self.price = price #: Its price when we enquired
        self.n_stops = n_stops #: How many stopovers there are on the journey
        self.carriers = carriers #: A list of carriers (in case there are several over the different stops)
        self.departure_location = departure_location #: The airport the plane leaves from as a code, eg 'LGW'
        self.arrival_location = arrival_location #: The airport the plane lands in, eg 'MAD'
        self.departure_date = departure_date #: When the plane takes off
        self.duration = duration #: How long the flight takes
        self.departure_time_of_day = departure_time_of_day #: When the flight leaves
        self.arrival_time_of_day = arrival_time_of_day #: When the flights arrives


    def represents_same_leg(self, other):
        '''
        Returns true if this object represents the same flight as other
        '''
        return self.carriers == other.carriers and\
        self.departure_location == other.departure_location and\
        self.arrival_location == other.arrival_location and\
        self.departure_date == other.departure_date


    def __repr__(self):
        return str(self.__dict__)


def pull_numbers(time: str, leg: dict) -> Leg:
    '''
    Takes a leg from the Expedia JSON and returns a more manageable object holding
    a subset of its data. 

    Args:
        time the timestamp for when the leg was saved. In %d-%m-%y_%H_%M format.
        leg a dict representing a 'leg' from the Expedia JSON file
    Returns:
        A leg object containing a subset of the data from the JSON file
    '''

    request_time = datetime.strptime(time, "%d-%m-%y_%H_%M")
    price = float(leg['price']['totalPriceAsDecimal'])
    n_stops = int(leg['stops'])
    # Always a list, in case there are multiple stops
    airline_codes = leg['carrierSummary']['airlineCodes'] # https://en.wikipedia.org/wiki/List_of_airline_codes
    departure_location = leg['departureLocation']['airportCode']
    arrival_location = leg['arrivalLocation']['airportCode']

    d = leg['departureTime']['isoStr']
    departure_date = dateutil.parser.parse(d)

    duration = leg['duration']
    delta = timedelta(hours=duration['hours'], minutes=duration['minutes'])

    departure_time_of_day = TimeOfDay(duration['departureTimeOfDay'])
    arrival_time_of_day = TimeOfDay(duration['arrivalTimeOfDay'])

    return Leg(request_time, price, n_stops, airline_codes, departure_location, arrival_location, departure_date, delta, departure_time_of_day, arrival_time_of_day)
