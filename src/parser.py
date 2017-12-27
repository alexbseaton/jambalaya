import downloader
import pprint
import pickle as pkl
from datetime import datetime
from datetime import timedelta
import dateutil.parser
from enum import Enum, unique


@unique
class TimeOfDay(Enum):
    morning = 'MORNING'
    afternoon = 'AFTERNOON'
    evening = 'EVENING'

    @staticmethod
    def from_string(string):
        for d in TimeOfDay:
            if d.value == string:
                return d
        raise ValueError("Unknown time of day: {}".format(string))


def load_example_legs():
    with open('../data/26-12-17_12_16.pkl', 'rb') as f:
        pickle = pkl.load(f)
    return pickle[0], iter(pickle[1].values())


def pull_numbers(time, leg):
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

    departure_time_of_day = TimeOfDay.from_string(duration['departureTimeOfDay'])
    arrival_time_of_day = TimeOfDay.from_string(duration['arrivalTimeOfDay'])

    return {'request time': request_time, 'price': price, 'n_stops': n_stops, 'carriers': airline_codes,
        'departure_location': departure_location, 'arrival_location': arrival_location, 'departure_date': departure_date,
        'duration': delta, 'departure_time_of_day': departure_time_of_day, 'arrival_time_of_day': arrival_time_of_day}


def create_dev_aids():
    '''
    Writes the key/value structure of a 'leg' to some text files in the ../data folder to make it a bit clearer
    what's going on.
    '''
    first_leg = next(load_example_legs()[1])
    with open('../data/key_structure.txt', 'w') as f:
        f.write(visualise(first_leg, 1))
    with open('../data/value_structure.txt', 'w') as f:
        pprint.pprint(first_leg, stream=f)


def visualise(dict_of_dicts: dict, n_nestings: int) -> str:
    result = ''
    for key, value in dict_of_dicts.items():
        result += key + ','
        if isinstance(value, dict): 
            result += '\n' + ('\t' * n_nestings) + '[' + visualise(value, n_nestings + 1) + ']\n'
        else: 
            result += '\n' + ('\t' * (n_nestings - 1))
    return result


if __name__ == '__main__':
    eg = load_example_legs()
    for leg in filter(lambda leg: leg['stops'] == 0, eg[1]):
        print(pull_numbers(eg[0], leg))