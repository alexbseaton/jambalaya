import requests
from bs4 import BeautifulSoup

url = "https://www.expedia.co.uk/Flights-Search?mode=search&paandi=true&trip=oneway&options=cabinclass%3Aeconomy%2Cno" \
      "penalty%3AN%2Csortby%3Aprice&passengers=children%3A0%2Cadults%3A1%2Cseniors%3A0%2Cinfantinlap%3AY&leg1=from%3A" \
      "London%2C%20England%2C%20UK%20(LGW-Gatwick)%2Cto%3AMadrid%2C%20Spain%20(MAD-Adolfo%20Suarez%20Madrid-Barajas)%" \
      "2Cdeparture%3A5%2F12%2F2017TANYT"


def scrape():
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    # print(soup.prettify)
    if "flex-card flex-listing flex-card-offer" in str(soup):
        print("it's there!")
    else:
        print("not there")

    # No worky :(
    the_divs = soup.find_all("div", class_="flex-card flex-listing flex-card-offer")
    if the_divs:
        print(the_divs[0])


if __name__ == '__main__':
    scrape()
