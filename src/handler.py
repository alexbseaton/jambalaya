import os
import datetime as dt
import json
import requests
from bs4 import BeautifulSoup
import sys
import logging
import traceback
import time
import itertools

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import alchemy_utils
import rds_config
import leg

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# Console handler
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)
# File handler
fh = logging.FileHandler('log.log')
fh.setLevel(logging.ERROR)
fh.setFormatter(formatter)
logger.addHandler(fh)


try:
    connection = 'mysql+pymysql://{user}:{password}@{host}/{db_name}'.format(user=rds_config.db_username, password=rds_config.db_password, host=rds_config.rds_host, db_name=rds_config.db_name)
    engine = create_engine(connection)
    alchemy_utils.Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
except Exception as e:
    logger.error("ERROR: Unexpected error: Could not connect to MySql instance.\t{}".format(e))
    sys.exit()


logger.info("SUCCESS: Connection to RDS mysql instance succeeded")
def scrape(n_tries, departure_airport, arrival_airport, departure_date):
    for i in range(n_tries):
        try:
            legs = get_legs(departure_airport, arrival_airport, departure_date)
            if legs == []:
                raise ValueError("No results")
            persist_legs(legs, departure_date)
            return 'Scraping successful'
        except Exception as e:
            logger.error('Attempt {} of {} failed. Retrying...'.format(i+1, n_tries))
            traceback.print_exc()
    return logger.error('All attempts failed for DEP:\t{}\nARR:\t{}\nDate:\t{}'.format(departure_airport, arrival_airport, departure_date))


def persist_legs(legs, departure_date):
    session = Session()
    try:
        session.add_all(legs)
        session.commit()
        logger.info('Committed')
    except:
        session.rollback()
        logger.error('Rollback')
        raise
    finally:
        session.close()


def get_legs(departure_airport, arrival_airport, departure_date):
    mmddyyyy_date = departure_date.strftime('%d/%m/%Y')
    url = "https://www.expedia.co.uk/Flights-Search?flight-type=on&starDate=14%2F01%2F2018&_xpid=11905%7C1&mode=search&trip=oneway&leg1=from:{0}to:{1}departure:{2}TANYT&passengers=children%3A0%2Cadults%3A1%2Cseniors%3A0%2Cinfantinlap%3AY&options=maxhops%3A0%2C".format(departure_airport, arrival_airport, mmddyyyy_date)

    logger.info('url:{}'.format(url))
    
    request_time = dt.datetime.now()
    response = requests.get(url)
    page = response.text
    soup = BeautifulSoup(page, 'html.parser')
    result = []
    for t in soup.find_all('li', {'class':'flight-module segment offer-listing'}):
        raw_duration = t.find('span', {'class':'total-duration duration-emphasis'}).contents[0].strip()
        d = dt.datetime.strptime(raw_duration, "%Hh %Mm")
        if (d.hour > 2): # don't save these long running ones
            continue
        duration = dt.timedelta(hours=d.hour, minutes=d.minute)
        raw_departure_time = t.find('span', {'data-test-id':'departure-time'}).contents[0].strip()
        departure_time = dt.datetime.combine(departure_date, dt.datetime.strptime(raw_departure_time, "%H:%M").time())
        raw_price = t.find('div', {'class':'price-column'}).attrs['data-test-price-per-traveler']
        price = float(raw_price.strip('£'))
        airline = t.find('span', {'data-test-id':'airline-name'}).contents[0].strip()
        result.append(leg.Leg(price=price, departure_location=departure_airport, arrival_location=arrival_airport, departure_date=departure_time, \
        request_time=request_time, duration=duration, airline=airline))
    return result


def main():
    departure = 'LGW'
    busy_airports = ['MAD', 'CDG', 'AMS', 'FCO', 'DUB']
    n_tries = 10
    day_count = 180
    for arrival in busy_airports:
        for departure_date in (dt.datetime.now() + dt.timedelta(days=n+1) for n in range(day_count)):
            scrape(n_tries, departure, arrival, departure_date)
            scrape(n_tries, arrival, departure, departure_date)


if __name__ == '__main__':
    main()
