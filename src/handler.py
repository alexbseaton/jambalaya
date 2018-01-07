import os
import datetime as dt
import json
import requests
from bs4 import BeautifulSoup
import sys
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import rds_config
import leg

logger = logging.getLogger()
logger.setLevel(logging.INFO)


try:
    connection = 'mysql+pymysql://{user}:{password}@{host}/{db_name}'.format(user=rds_config.db_username, password=rds_config.db_password, host=rds_config.rds_host, db_name=rds_config.db_name)
    engine = create_engine(connection, echo=True)
    #alchemy_utils.Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
except Exception as e:
    logger.error("ERROR: Unexpected error: Could not connect to MySql instance.\t{}".format(e))
    sys.exit()


logger.info("SUCCESS: Connection to RDS mysql instance succeeded")
def scrape(n_tries, departure_airport, arrival_airport, departure_date):
    for i in range(n_tries):
        try:
            raw_json = get_raw_json(departure_airport, arrival_airport, departure_date)
            legs = json.loads(raw_json["content"])['legs']
            if legs == {}:
                raise ValueError("No data in script - maybe it sent us to a reCaptcha?")
            persist_legs(legs, departure_date)
            return
        except ValueError:
            print('Attempt {} of {} failed. Retrying...'.format(i+1, n_tries))


def persist_legs(legs, departure_date):
    request_time = dt.datetime.now()
    session = Session()
    all_legs = [leg.create_leg(request_time, leg_json) for leg_json in legs.values()]
    
    # Sanity check- the stuff we're saving should have the departure date we asked for
    for l in all_legs:
        print('Departure date: \n{}\n\n'.format(l.departure_date))
        print('Expected:{}'.format(departure_date))
        assert l.departure_date.date() == departure_date.date()
    
    try:
        session.add_all([l for l in all_legs if l.n_stops == 0])
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def get_raw_json(departure_airport, arrival_airport, departure_date):
    mmddyyyy_date = departure_date.strftime('%m/%d/%Y')
    url =   "https://www.expedia.com/Flights-Search?trip=oneway&leg1=from:"\
            "{0},to:{1},departure:{2}TANYT&passengers=adults:1,children:0,seniors:0,infantinlap:Y&options=cabinclass%3A"\
            "economy&mode=search&origref=www.expedia.com".format(departure_airport, arrival_airport, mmddyyyy_date)
    
    print('url:\n{}\n\n'.format(url))
    
    page = requests.get(url).text
    soup = BeautifulSoup(page, 'html.parser')
    return json.loads(soup.find(id="cachedResultsJson").string)


def main():
    departure_airport = 'LGW'
    arrival_airport = 'MAD'
    n_tries = 3
    day_count = 1
    for departure_date in (dt.datetime.now() + dt.timedelta(days=n+7) for n in range(day_count)):
        scrape(n_tries, departure_airport, arrival_airport, departure_date)

if __name__ == '__main__':
    main()
