import boto3
import io
import pickle as pkl

def download():
    ''' 
    Probably want the API to be something like given this date, return me a list of all the
    things we saved that day, seeing as we won't know the exact time.
    '''
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('alex-jambalaya-json-dumps')
    key = 'scrape_26-12-17_12_38.pkl'
    write_to = io.BytesIO()
    bucket.download_fileobj(key, write_to)
    write_to.seek(0) # got to drag the stream back to the beginning
    return pkl.load(write_to)


if __name__ == '__main__':
    print(download())