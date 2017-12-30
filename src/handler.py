import os
import datetime as dt
import json
import requests
from bs4 import BeautifulSoup
import boto3
import pickle as pkl
import io

from scrape_parser import Leg

s3_client = boto3.client('s3')


def my_handler(event, context):
    S3BUCKET = os.environ['s3_bucket']
    n_tries = int(os.environ['n_tries'])
    departure_airport = os.environ['departure_airport']
    arrival_airport = os.environ['arrival_airport']
    departure_date = os.environ['mmddyyyy_date']
    scrape(n_tries, S3BUCKET, departure_airport, arrival_airport, departure_date)
    return {'message': 'Ran ok'}


def scrape(n_tries, s3_bucket, departure_airport, arrival_airport, departure_date):
    for i in range(n_tries):
        try:
            raw_json = get_raw_json(departure_airport, arrival_airport, departure_date)
            legs = json.loads(raw_json["content"])['legs']
            if legs == {}:
                raise ValueError("No data in script - maybe it sent us to a reCaptcha?")
            request_time = dt.datetime.now()
            flight_data = [Leg(request_time, leg) for leg in legs.values()]
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
