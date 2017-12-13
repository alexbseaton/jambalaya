from datetime import datetime
from urllib.request import urlopen
import requests
import json
from lxml import html
import os
import datetime as dt

SITE = os.environ['site']  # URL of the site to check, stored in the site environment variable
EXPECTED = os.environ['expected']  # String expected to be on the page, stored in the expected environment variable


def validate(res):
    '''Return False to trigger the canary

    Currently this simply checks whether the EXPECTED string is present.
    However, you could modify this to perform any number of arbitrary
    checks on the contents of SITE.
    '''
    return EXPECTED in res


def lambda_handler(event, context):
    print('Checking {} at {}...'.format(SITE, event['time']))
    try:
        if not validate(str(urlopen(SITE).read())):
            raise Exception('Validation failed')
    except:
        print('Check failed!')
        raise
    else:
        print('Check passed!')

        parse('LGW', 'MAD', '12/19/2017', test=False)
        return event['time']
    finally:
        print('Check complete at {}'.format(str(datetime.now())))


def parse(source, destination, date, test=False):
    n_tries = 1 if test else 5
    for i in range(n_tries):
        try:
            raw_json = get_raw_json(source, destination, date, test)
            timestamp = dt.datetime(2017, 12, 19, 17) if test else dt.datetime.now()
            timestamp = timestamp.strftime("%d-%m-%y_%H_%M")
            flight_data = (timestamp, json.loads(raw_json["content"])['legs'])

            print(flight_data)
            return

        except ValueError:
            print('Attempt {} of {} failed. Retrying...'.format(i + 1, n_tries))


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
