# jambalaya

## Current Goal

Simple:

Support graphing price histories given an arbitrary collection of flights (ATM it is assumed all will be between the same airports)

Hard:

Make a predictive model where given:

* departure location, arrival location, departure date and an airline (ie, a particular flight) and also 
* a datetime representing when we ask for a price from the search engine (the request time), 

predicts the price that the search engine will yield. This is its guess of how much a ticket would be if we
bought it at that time. We can use that to deduce the (predicted) best time to buy a ticket.

First step: Focus on just one flight (so only around 60 examples) and see if we can get anything vaguely sensible working.

## Installation
You need a 64 bit Python 3 installation.

Install Pipenv.

Go to the jambalaya folder and run:

* *pipenv install --dev*
* *pipenv shell*

If you want to run handler.py, install PhantomJS and put it on your PATH, but it probably
doesn't need any more work and the server runs it so we don't need to run it locally.
