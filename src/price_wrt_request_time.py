""" Tracks the price of a particular flight over our entire history of requests, to see which day would
have been best to buy a ticket for it.
"""

import handler
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
from leg import Leg

session = handler.Session()


def get_prices_for_flight(departure_location: str, arrival_location: str, airline: str, departure_date: dt.datetime, save_figure=False) -> pd.DataFrame:
    """Gets all the prices we have recorded for a particular flight.

    By default, this also saves a graph of those prices.

    Args:
        departure_location: The airport the plane leaves from, eg 'LGW'.
        arrival_location: The airport the plane lands in, eg 'MAD'.
        airline: The airline running the flight, see the DB for the exact format of these.
        departure_date: When the flight leaves. Seconds and smaller are ignored.
        save_figure: Whether to save a graph of the prices in the data folder.

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

    if l.count() == 0:
        raise ValueError('No matching flight found')

    print('Getting prices for the flight with {} leaving at {} from {} to {}.\nThere are {} entries.'\
        .format(airline, departure_date, departure_location, arrival_location, l.count()))

    data = pd.read_sql(l.statement, l.session.bind)

    if save_figure:
        data.plot(x='request_time', y='price')
        plt.ylabel('Price (£)')
        plt.title('{} to {}, {}, leaving {}'.format(\
            departure_location, arrival_location, airline, departure_date))
        plt.savefig('../data/{}-{}-{}.png'.format(\
            departure_location, arrival_location, departure_date.strftime('%H--%M-{}'.format(airline.replace(' ', '')))))
        #plt.show()

    return data


if __name__ == '__main__':
    # TODO Generalise this: I want to be able to draw any price history graph like this given an arbitrary collection of flights
    aer_lingus = get_prices_for_flight('LGW', 'DUB', 'Aer Lingus', dt.datetime(2018, 3, 22, 10, 55))
    ryanair = get_prices_for_flight('LGW', 'DUB', 'Ryanair', dt.datetime(2018, 3, 22, 9, 40))
    ax = aer_lingus.plot(x='request_time', y='price')
    ryanair.plot(x='request_time', y='price', ax=ax)
    ax.legend(['Aer Lingus 1055', 'Ryanair 0940'])
    plt.title('LGW to DUB 22/3')
    plt.savefig('../data/ryanair_and_lingus_on_same_axes.png')
    plt.show()
