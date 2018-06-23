""" Tracks the price of a particular flight over our entire history of requests, to see which day would
have been best to buy a ticket for it.
"""

import handler
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
from leg import Leg

session = handler.Session()


def get_prices_for_flight(departure_airport: str, arrival_airport: str, airline: str, departure_date: dt.datetime) -> pd.DataFrame:
    """Gets all the prices we have recorded for a particular flight.

    Args:
        departure_location: The airport the plane leaves from, eg 'LGW'.
        arrival_location: The airport the plane lands in, eg 'MAD'.
        airline: The airline running the flight, see the DB for the exact format of these.
        departure_date: When the flight leaves. Seconds and smaller are ignored.

    Returns:
        A Pandas dataframe holding two columns: the 'price' for each 'request_time'.

    Raises:
        ValueError: If we don't have data for the flight you've specified
    """
    l = session.query(Leg.request_time, Leg.price).\
        filter(Leg.departure_location == departure_airport).\
        filter(Leg.arrival_location == arrival_airport).\
        filter(Leg.airline == airline).\
        filter(Leg.departure_date == departure_date)

    if not l.count():
        raise ValueError('No matching flight found')

    print('Getting prices for the flight with {} leaving at {} from {} to {}.\nThere are {} entries.'\
        .format(airline, departure_date, departure_airport, arrival_airport, l.count()))

    return pd.read_sql(l.statement, l.session.bind)


def draw_on_same_axes(flights, show_plot=True, save_fig=True):
    """Plots the prices of flights between two airports for the flights specified.

    By default, this saves a graph of those prices.

    An example invocation is:

    Example:
        >>>     draw_on_same_axes([{'airline': 'Aer Lingus', 'departure_date': dt.datetime(2018, 3, 22, 10, 55), 'departure_airport': 'LGW', 'arrival_airport': 'DUB'}, \
    {'airline': 'Ryanair', 'departure_date': dt.datetime(2018, 3, 22, 9, 40), 'departure_airport': 'LGW', 'arrival_airport': 'DUB'}])

    Args:
        flights: A list of dicts, see the example invocation. Departure date is to the nearest minute
        show_plot: Whether to show the graph on-screen when this function is invoked
        save_figure: Whether to save a graph of the prices in the data folder

    Returns:
        None

    Raises:
        ValueError: If we don't have data for one or more of the flights you've specified
    """
    first = get_prices_for_flight(**flights[0])
    ax = first.plot(x='request_time', y='price')
    legend = [_stringify(flight) for flight in flights]
    plt.title('Flight history')
    for flight in flights[1:]:
        data = get_prices_for_flight(**flight)
        data.plot(x='request_time', y='price', ax=ax)

    ax.legend(legend)
    if save_fig:
        plt.savefig('../data/price_history_{}'.format(dt.datetime.now().strftime('%d-%m-%y_%H-%M-%S')))
    if show_plot:
        plt.show()


def _stringify(flight):
    return '{} {} from {} to {}'.format(flight['airline'], flight['departure_date'].strftime('%H%M'), \
    flight['departure_airport'], flight['arrival_airport'])
    

if __name__ == '__main__':
    draw_on_same_axes([{'airline': 'Aer Lingus', 'departure_date': dt.datetime(2018, 3, 22, 10, 55), 'departure_airport': 'LGW', 'arrival_airport': 'DUB'}, \
    {'airline': 'Ryanair', 'departure_date': dt.datetime(2018, 3, 22, 9, 40), 'departure_airport': 'LGW', 'arrival_airport': 'DUB'}])
