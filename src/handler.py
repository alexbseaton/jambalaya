import datetime as dt
import json
import requests
from bs4 import BeautifulSoup
import boto3
import pickle as pkl

s3_client = boto3.client('s3')

def my_handler(event, context):
    url = "https://www.expedia.com/Flights-Search?trip=oneway&leg1=from:{0},to:{1},departure:{2}TANYT&passengers=adults:1,children:0,seniors:0,infantinlap:Y&options=cabinclass%3Aeconomy&mode=search&origref=www.expedia.com".format(
        'LGW', 'MAD', '2/17/2018')
    page = requests.get(url).text
    soup = BeautifulSoup(page, 'html.parser')
    raw_json = json.loads(soup.find(id="cachedResultsJson").string)
    timestamp = dt.datetime.now().strftime("%d-%m-%y_%H_%M")
    flight_data = (timestamp, json.loads(raw_json["content"])['legs'])
    filepath = '/tmp/'+timestamp
    with open(filepath, 'wb') as f:
        pkl.dump(flight_data, f)
    s3_client.upload_file(filepath, 'alex-jambalaya-json-dumps', "scrape_{}.pkl".format(timestamp))
    print(flight_data)
    return { 
        'message' : "ran OK"
    } 


if __name__ == '__main__':
    my_handler(None, None)