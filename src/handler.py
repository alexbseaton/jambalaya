import os
import datetime as dt
import json
import requests
from bs4 import BeautifulSoup
import boto3
import pickle as pkl

s3_client = boto3.client('s3')
S3BUCKET = os.environ['s3_bucket']


def my_handler(event, context):
    n_tries = event['n_tries']
    for i in range(n_tries):
        raw_json = get_raw_json()
        flight_data = (dt.datetime.now().strftime("%d-%m-%y_%H_%M"), json.loads(raw_json["content"])['legs'])
        save_flight_data(flight_data, '/tmp/' + flight_data[0], S3BUCKET)

        return {'message' : "ran OK"}

def get_raw_json():
        url =   "https://www.expedia.com/Flights-Search?trip=oneway&leg1=from:"\
                "{0},to:{1},departure:{2}TANYT&passengers=adults:1,children:0,seniors:0,infantinlap:Y&options=cabinclass%3A"\
                "economy&mode=search&origref=www.expedia.com".format('LGW', 'MAD', '2/17/2018')
        page = requests.get(url).text
        soup = BeautifulSoup(page, 'html.parser')

        return json.loads(soup.find(id="cachedResultsJson").string)

def save_flight_data(flight_data, filepath, s3_bucket):
    with open(filepath, 'wb') as f:
        pkl.dump(flight_data, f)
    s3_client.upload_file(filepath, s3_bucket, "scrape_{}.pkl".format(flight_data[0]))
    print(flight_data)


if __name__ == '__main__':
    my_handler(None, None)
