import requests
import json
from bs4 import BeautifulSoup
import os
import pickle as pkl
import datetime as dt
import requests

def parse(source, destination, date, test=False):
    n_tries = 1 if test else 5
    for i in range(n_tries):
        try:
            raw_json = get_raw_json(source, destination, date, test)
            timestamp = dt.datetime(2017, 12, 19, 17) if test else dt.datetime.now()
            timestamp = timestamp.strftime("%d-%m-%y_%H_%M")
            flight_data = (timestamp, json.loads(raw_json["content"])['legs'])
            filepath = os.path.join(os.pardir, 'data', 'scraped_data', 'scrape_' + str(timestamp))
            with open(filepath, 'wb') as f:
                pkl.dump(flight_data, f)

            print(flight_data)
            return

        except ValueError:
            print('Attempt {} of {} failed. Retrying...'.format(i+1, n_tries))


def get_raw_json(source, destination, date, test=False):
    if test:
        page = open(os.path.join(os.pardir, 'data', 'test_data', 'example_page_source.html'))
    else:
        url = "https://www.expedia.com/Flights-Search?trip=oneway&leg1=from:{0},to:{1},departure:{2}TANYT&passengers=adults:1,children:0,seniors:0,infantinlap:Y&options=cabinclass%3Aeconomy&mode=search&origref=www.expedia.com".format(
            source, destination, date)
        page = requests.get(url).text

    soup = BeautifulSoup(page, 'html.parser')
    return json.loads(soup.find(id="cachedResultsJson").string)


if __name__ == '__main__':
    parse('LGW', 'MAD', '2/17/2018', True)
