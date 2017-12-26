import os
import sys
sys.path.append('../src')
from handler import scrape

if __name__ == '__main__':
    print(scrape(5, 'alex-jambalaya-json-dumps'))
