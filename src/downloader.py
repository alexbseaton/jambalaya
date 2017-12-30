import boto3
import io
import pickle as pkl
import datetime as dt
from functools import partial
from typing import List, Tuple

Scrape = List[Tuple[str, dict]]


def download_item(key: str) -> Scrape:
    ''' 
    Loads the item in the bucket with the given key.

    The key must refer to a .pkl file.

    Args:
        key (str) The name of the item you wish to download
    Returns:
        The in-memory representation of the pickled item you downloaded 
    '''
    assert key.endswith('.pkl')
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('alex-jambalaya-json-dumps')
    write_to = io.BytesIO()
    bucket.download_fileobj(key, write_to)
    write_to.seek(0)  # got to drag the stream back to the beginning
    return pkl.load(write_to)


def download_all_on_day(date: dt.date, file: str = None) -> List[Scrape]:
    '''
    Downloads all the scrapes that were made on date.

    Args:
        date: This method will download all the scrapes made on the supplied date
        write_to_file: The file to write the pickled result of this function to

    Returns:
        A list of the scrapes made on date, which are tuples of the date the
        request was made in "%d-%m-%y_%H_%M" format and the actual payload of 
        the request as a dict.
    '''
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('alex-jambalaya-json-dumps')

    result = []
    for obj in filter(partial(_is_saved_on_date, date), bucket.objects.all()):
        result.append(download_item(obj.key))

    if file:
        with open(file, 'wb') as f:
            pkl.dump(result, f)
    
    return result


def _is_saved_on_date(date, object_summary): 
    try:
        request_time = dt.datetime.strptime(object_summary.key, "scrape_%d-%m-%y_%H_%M.pkl")
        return request_time.date() == date
    except ValueError: # Might not be a scrape
        return False
