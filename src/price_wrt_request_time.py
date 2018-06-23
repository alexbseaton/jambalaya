""" Tracks the price of a particular flight over our entire history of requests, to see which day would
have been best to buy a ticket for it.
"""

import handler
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
from leg import Leg

session = handler.Session()


def get_prices_for_flight(departure_location: str, arrival_location: str, airline: str, departure_date: dt.datetime) -> pd.DataFrame:
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
        filter(Leg.departure_location == departure_location).\
        filter(Leg.arrival_location == arrival_location).\
        filter(Leg.airline == airline).\
        filter(Leg.departure_date == departure_date)

    if not l.count():
        raise ValueError('No matching flight found')

    print('Getting prices for the flight with {} leaving at {} from {} to {}.\nThere are {} entries.'\
        .format(airline, departure_date, departure_location, arrival_location, l.count()))

    return pd.read_sql(l.statement, l.session.bind)


def draw_on_same_axes(departure_location, arrival_location, airlines_and_dates, show_plot=True, save_fig=True):
    """Plots the prices of flights between two airports for the flights specified.

    By default, this saves a graph of those prices.

    An example invocation is:

    Example:
        >>> draw_on_same_axes('LGW', 'DUB', [('Aer Lingus', dt.datetime(2018, 3, 22, 10, 55)), ('Ryanair', dt.datetime(2018, 3, 22, 9, 40))])

    Args:
        departure_location: The airport the plane leaves from, eg 'LGW'.
        arrival_location: The airport the plane lands in, eg 'MAD'.
        airlines_and_dates: A list of tuples whose first elements are the airline running the flight, see the DB for the exact format of those, 
        and whose second elements are the departure dates of the flight to the nearest minute.
        show_plot: Whether to show the graph on-screen when this function is invoked
        save_figure: Whether to save a graph of the prices in the data folder.

    Returns:
        None

    Raises:
        ValueError: If we don't have data for one or more of the flights you've specified
    """
    first = get_prices_for_flight(departure_location, arrival_location, airlines_and_dates[0][0], airlines_and_dates[0][1])
    ax = first.plot(x='request_time', y='price')
    legend = ['{} {}'.format(airlines_and_dates[0][0], airlines_and_dates[0][1].strftime('%H%M'))]
    day = airlines_and_dates[0][1].strftime('%d-%m')
    plt.title('{} to {} {}'.format(departure_location, arrival_location, day))
    for ad in airlines_and_dates[1:]:
        data = get_prices_for_flight(departure_location, arrival_location, ad[0], ad[1])
        data.plot(x='request_time', y='price', ax=ax)
        legend.append('{} {}'.format(ad[0], ad[1].strftime('%H%M')))
    ax.legend(legend)
    if save_fig:
        plt.savefig('../data/{}-{}--{}'.format(departure_location, arrival_location, day))
    if show_plot:
        plt.show()
    

if __name__ == '__main__':
    draw_on_same_axes('LGW', 'DUB', [('Aer Lingus', dt.datetime(2018, 3, 22, 10, 55)), ('Ryanair', dt.datetime(2018, 3, 22, 9, 40))])
