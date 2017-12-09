import requests
import json
from lxml import html
import os


def parse(source, destination, date):
    for i in range(5):
        try:
            url = "https://www.expedia.com/Flights-Search?trip=oneway&leg1=from:{0},to:{1},departure:{2}TANYT&passengers=adults:1,children:0,seniors:0,infantinlap:Y&options=cabinclass%3Aeconomy&mode=search&origref=www.expedia.com".format(source,destination,date)
            print(url)
            response = requests.get(url)
            parser = html.fromstring(response.text)
            json_data_xpath = parser.xpath("//script[@id='cachedResultsJson']//text()")
            raw_json = json.loads(json_data_xpath[0])
            with open(os.path.join(os.pardir, 'data', 'test_data_130e4a71ac38db2b22c866088d5fe135'), 'w') as f:
                 json.dump(raw_json, f)
            flight_data = json.loads(raw_json["content"])
            total_prices = dict()
            for leg in flight_data['legs'].keys():
                total_prices[leg] = dict()
                total_prices[leg]['totalPriceAsDecimal'] = flight_data['legs'][leg]['price']['totalPriceAsDecimal']

            print(flight_data['legs']['130e4a71ac38db2b22c866088d5fe135'])

            assert flight_data['legs']['130e4a71ac38db2b22c866088d5fe135']['carrierSummary']['airlineName'] == 'Air Europa'

            print(total_prices['130e4a71ac38db2b22c866088d5fe135']['totalPriceAsDecimal'])



            return 'Finished'

        except ValueError:
            print('Retrying')

if __name__ == '__main__':
    parse('LGW', 'MAD', '12/19/2017')
