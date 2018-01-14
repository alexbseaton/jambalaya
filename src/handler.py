import os
import datetime as dt
import json
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

from selenium import webdriver

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

driver = webdriver.PhantomJS()

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


def has_data_test_id(id, tag):
    key = "data-test-id"
    return key in tag.attrs and tag.attrs[key] == id


def get_legs(departure_airport, arrival_airport, departure_date):
    mmddyyyy_date = departure_date.strftime('%d/%m/%Y')
    url = "https://www.expedia.co.uk/Flights-Search?flight-type=on&starDate=14%2F01%2F2018&_xpid=11905%7C1&mode=search&trip=oneway&leg1=from:{0}to:{1}departure:{2}TANYT&passengers=children%3A0%2Cadults%3A1%2Cseniors%3A0%2Cinfantinlap%3AY&options=maxhops%3A0%2C".format(departure_airport, arrival_airport, mmddyyyy_date)
    logger.info('url:{}'.format(url))
    
    driver.get(url)
    time.sleep(5) # let the JS run
    request_time = dt.datetime.now()
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')

    result = []
    for t in soup.find_all('li', {'class':'flight-module segment offer-listing'}):
        # Duration
        raw_duration = t.find(lambda d: has_data_test_id("duration", d)).contents[0].strip()
        d = dt.datetime.strptime(raw_duration, "%Hh %Mm")
        if (d.hour > 2): # don't save these long running ones
            continue
        duration = dt.timedelta(hours=d.hour, minutes=d.minute)
        # Departure time
        raw_departure_time = t.find(lambda d: has_data_test_id('departure-time', d)).contents[0].strip()
        departure_time = dt.datetime.combine(departure_date, dt.datetime.strptime(raw_departure_time, "%H:%M").time())
        # Price per traveller
        ppt = 'data-test-price-per-traveler'
        raw_price = t.find(lambda d: ppt in d.attrs).attrs[ppt]
        price = float(raw_price.strip('£'))
        # Airline
        airline = t.find(lambda d: has_data_test_id('airline-name', d)).contents[0].strip()
        # Create the record
        result.append(leg.Leg(price=price, departure_location=departure_airport, arrival_location=arrival_airport, departure_date=departure_time, \
        request_time=request_time, duration=duration, airline=airline))

    return result


def main():
    departure = 'LGW'
    busy_airports = ['MAD', 'CDG', 'AMS', 'FCO', 'DUB']
    n_tries = 1
    day_count = 1
    for arrival in busy_airports:
        for departure_date in (dt.datetime.now() + dt.timedelta(days=n+1) for n in range(day_count)):
            scrape(n_tries, departure, arrival, departure_date)
            scrape(n_tries, arrival, departure, departure_date)


if __name__ == '__main__':
    main()
