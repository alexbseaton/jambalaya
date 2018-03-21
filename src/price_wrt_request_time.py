""" Tracks the price of a particular flight over our entire history of requests, to see which day would
have been best to buy a ticket for it.
"""

from handler import engine
import pandas as pd
import matplotlib.pyplot as plt

statement = """
    SELECT * FROM leg
    WHERE departure_location = 'LGW'
    AND arrival_location = 'DUB'
    AND airline = 'Aer Lingus'
    AND departure_date = '2018-03-22 10:55:00'
    """

with engine.connect() as con:
    same_flight = pd.read_sql(statement, con)

same_flight.plot(x='request_time', y='price')
plt.ylabel('Price (£)')
plt.title('Gatwick to Dublin, Aer Lingus, leaving 1055 21/3')
plt.savefig('../data/LGW-DUB-21-3.png')