import os
import datetime as dt
import json
import requests
from bs4 import BeautifulSoup
import boto3
import pickle as pkl
import io

import sys
import logging
import rds_config
import pymysql
import scrape_parser

#rds settings
name = rds_config.db_username
password = rds_config.db_password
db_name = rds_config.db_name

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')

try:
    conn = pymysql.connect(rds_config.rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)
    logger.info("SUCCESS: Connection to RDS mysql instance succeeded")
except:
    logger.error("ERROR: Unexpected error: Could not connect to MySql instance.")
    sys.exit()

def my_handler(event, context):
    select_query()
    S3BUCKET = os.environ['s3_bucket']
    n_tries = int(os.environ['n_tries'])
    departure_airport = os.environ['departure_airport']
    arrival_airport = os.environ['arrival_airport']
    departure_date = os.environ['mmddyyyy_date']
    scrape(n_tries, S3BUCKET, departure_airport, arrival_airport, departure_date)
    return {'message': 'Ran ok'}

def select_query():
    
    with conn.cursor() as cur:
        # The first time that you run this, create the table first
        #cur.execute("create table Employee3 ( EmpID  int NOT NULL, Name varchar(255) NOT NULL, PRIMARY KEY (EmpID))")  
        #cur.execute('insert into Employee3 (EmpID, Name) values(1, "Joe")')
        #cur.execute('insert into Employee3 (EmpID, Name) values(2, "Bob")')
        #cur.execute('insert into Employee3 (EmpID, Name) values(3, "Mary")')
        #conn.commit()
        cur.execute("select * from Employee3")
        item_count = 0
        for row in cur:
            item_count += 1
            logger.info(row)
            print(row)


def scrape(n_tries, s3_bucket, departure_airport, arrival_airport, departure_date):
    for i in range(n_tries):
        try:
            raw_json = get_raw_json(departure_airport, arrival_airport, departure_date)
            legs = json.loads(raw_json["content"])['legs']
            if legs == {}:
                raise ValueError("No data in script - maybe it sent us to a reCaptcha?")
            request_time = dt.datetime.now()
            flight_data = [scrape_parser.create_leg(request_time, leg) for leg in legs.values()]
            save_flight_data(request_time, flight_data, s3_bucket)
            print(flight_data)
            return flight_data
        except ValueError:
            print('Attempt {} of {} failed. Retrying...'.format(i+1, n_tries))


def get_raw_json(departure_airport, arrival_airport, departure_date):
    url =   "https://www.expedia.com/Flights-Search?trip=oneway&leg1=from:"\
            "{0},to:{1},departure:{2}TANYT&passengers=adults:1,children:0,seniors:0,infantinlap:Y&options=cabinclass%3A"\
            "economy&mode=search&origref=www.expedia.com".format(departure_airport, arrival_airport, departure_date)
    page = requests.get(url).text
    soup = BeautifulSoup(page, 'html.parser')
    return json.loads(soup.find(id="cachedResultsJson").string)


def save_flight_data(request_time, flight_data, s3_bucket):
    filename = "scrape_{}.pkl".format(request_time.strftime("%d-%m-%y_%H_%M"))
    dump_to = io.BytesIO()
    pkl.dump(flight_data, dump_to)
    dump_to.seek(0) # got to drag the stream back to the beginning
    s3_client.upload_fileobj(dump_to, s3_bucket, filename)


if __name__ == '__main__':
    my_handler(None, None)
