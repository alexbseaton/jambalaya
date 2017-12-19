import requests
import json
from lxml import html
import os
import pickle as pkl
import datetime as dt


def parse(source, destination, date, test=False):
    n_tries = 1 if test else 5
    for i in range(n_tries):
        try:
            raw_json = get_raw_json(source, destination, date, test)
            timestamp = dt.datetime(2017, 12, 19, 17) if test else dt.datetime.now()
            timestamp = timestamp.strftime("%d-%m-%y_%H_%M")
            flight_data = (timestamp, json.loads(raw_json["content"])['legs'])
            filename = 'scrape_' + str(timestamp)
            filepath = os.path.join(os.pardir, 'data', 'scraped_data', filename)
            with open(filepath, 'wb') as f:
                pkl.dump(flight_data, f)

            print(flight_data)
            return

        except ValueError:
            print('Attempt {} of {} failed. Retrying...'.format(i+1, n_tries))


def get_raw_json(source, destination, date, test):
    if test:
        with open(os.path.join(os.pardir, 'data', 'test_data', 'test_data_130e4a71ac38db2b22c866088d5fe135'), 'r') as f:
            raw_json = json.load(f)
    else:
        url = "https://www.expedia.com/Flights-Search?trip=oneway&leg1=from:{0},to:{1},departure:{2}TANYT&passengers=adults:1,children:0,seniors:0,infantinlap:Y&options=cabinclass%3Aeconomy&mode=search&origref=www.expedia.com".format(
            source, destination, date)
        print(url)
        response = requests.get(url)
        parser = html.fromstring(response.text)
        json_data_xpath = parser.xpath("//script[@id='cachedResultsJson']//text()")
        raw_json = json.loads(json_data_xpath[0])

    return raw_json


def save_json(raw_json):
    with open(os.path.join(os.pardir, 'data', 'test_data_130e4a71ac38db2b22c866088d5fe135'), 'w') as f:
        json.dump(raw_json, f)


if __name__ == '__main__':
    parse('LGW', 'MAD', '2/19/2018')
