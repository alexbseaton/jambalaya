from handler import Session
from leg import Leg
from datetime import datetime
from datetime import date
import matplotlib.pyplot as plt
import matplotlib.dates as mpldates

session = Session()

def similar_flights(flight, all_flights):
    return [f for f in all_flights if f.represents_same_leg(flight)]

l = session.query(Leg).\
    filter(Leg.departure_location == 'LGW').\
    filter(Leg.arrival_location == 'DUB').\
    filter(Leg.departure_date <= datetime(2018,6,5)).\
    filter(Leg.departure_date >= datetime(2018,6,4))


grouped = []
matched = {leg:False for leg in l}
for leg in l:
    if matched[leg]:
        continue
    sim = similar_flights(leg, l)
    grouped.append(sim)
    for s in sim:
        matched[s] = True

for grp in grouped:
    if (len(grp)) > 1:
        multiple = grp

dep = l[0].departure_date
same_flight = [d for d in l if d.departure_date == dep]
dates = [mpldates.date2num(d.departure_date) for d in l if d.airline == 'Aer Lingus']
values = [d.price for d in l if d.airline == 'Aer Lingus']


plt.plot_date(dates, values)

print(multiple)

plt.show()
