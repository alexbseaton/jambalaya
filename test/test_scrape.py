import os
import sys
sys.path.append('..')

from src.handler import scrape

os.environ['s3_bucket'] = 'alex-jambalaya-json-dumps'


page = open(os.path.join(os.pardir, 'data', 'test_data', 'example_page_source.html'))


if __name__ == '__main__':
    scrape(5, os.environ['s3_bucket'])
