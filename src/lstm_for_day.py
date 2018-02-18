"""
Make an LSTM model based on a day's requests.

Most of the code is just lifted from
https://machinelearningmastery.com/multivariate-time-series-forecasting-lstms-keras/

"""
from leg import Leg
import pickle as pkl
from datetime import datetime
import pandas as pd
from sklearn.preprocessing import LabelEncoder # TODO change to OHE
from math import sqrt
from numpy import concatenate
from matplotlib import pyplot
from pandas import read_csv
from pandas import DataFrame
from pandas import concat
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error
from keras.models import Sequential
import keras.models
from keras.layers import Dense
from keras.layers import LSTM


def save(path: str, date_after: datetime, date_before: datetime):
    """
    Save requests made between two dates to a pickled dataframe.
    Arguments:
        path: The path to save to
        date_after: Requests falling on or after this date will be saved
        date_before: Requests falling before this date will be saved
    Returns:
        None
    """
    from handler import Session
    session = Session()
    query = session.query(Leg).\
        filter(Leg.request_time >= date_after).\
        filter(Leg.request_time < date_before)

    with open(path, 'wb') as f:
        df = pd.read_sql(query.statement, session.bind)
        pkl.dump(df, f)


def load(path: str):
    """
    Loads a pickled dataframe saved at path.
    Arguments:
        path: 
    """
    with open(path, 'rb') as f:
        return pkl.load(f)


def series_to_supervised(data, n_in=1, n_out=1, dropnan=True):
	"""
	Frame a time series as a supervised learning dataset.
	Arguments:
		data: Sequence of observations as a list or NumPy array.
		n_in: Number of lag observations as input (X).
		n_out: Number of observations as output (y).
		dropnan: Boolean whether or not to drop rows with NaN values.
	Returns:
		Pandas DataFrame of series framed for supervised learning.
	"""
	n_vars = 1 if type(data) is list else data.shape[1]
	df = DataFrame(data)
	cols, names = list(), list()
	# input sequence (t-n, ... t-1)
	for i in range(n_in, 0, -1):
		cols.append(df.shift(i))
		names += [('var%d(t-%d)' % (j+1, i)) for j in range(n_vars)]
	# forecast sequence (t, t+1, ... t+n)
	for i in range(0, n_out):
		cols.append(df.shift(-i))
		if i == 0:
			names += [('var%d(t)' % (j+1)) for j in range(n_vars)]
		else:
			names += [('var%d(t+%d)' % (j+1, i)) for j in range(n_vars)]
	# put it all together
	agg = concat(cols, axis=1)
	agg.columns = names
	# drop rows with NaN values
	if dropnan:
		agg.dropna(inplace=True)
	return agg


def load_data(path: str) -> tuple:
	"""
	Loads data in a format ready to be fed to a model.
	Arguments:
	    path: Path to a pickled dataframe holding the Leg data
	Returns:
	    A tuple containing train_X, train_Y, test_X, test_Y
	"""
	df = load(path)

	# Data prep: strings to integer labels and dates to ints
	df.drop('id', axis=1, inplace=True)
	df.drop('request_time', axis=1, inplace=True)
	df.sort_values(by='departure_date', inplace=True)
	encoder = LabelEncoder()
	df['duration'] = df['duration'].apply(lambda dur: dur.total_seconds())
	df['departure_date'] = df['departure_date'].apply(lambda ts: ts.timestamp())
	for col in ['departure_location', 'arrival_location', 'airline']:
		df[col] = encoder.fit_transform(df[col])
	values = df.values
	values = values.astype('float32')

	# normalize features
	scaled = MinMaxScaler().fit_transform(values)

	reframed = series_to_supervised(scaled)
	# split into train and test sets
	values = reframed.values
	n_train = values.shape[0] - 1000
	train = values[:n_train, :]
	test = values[n_train:, :]
	# split into input and outputs
	train_X, train_y = train[:, 1:], train[:, 0]
	test_X, test_y = test[:, 1:], test[:, 0]
	# reshape input to be 3D [samples, timesteps, features]
	train_X = train_X.reshape((train_X.shape[0], 1, train_X.shape[1]))
	test_X = test_X.reshape((test_X.shape[0], 1, test_X.shape[1]))
	print(train_X.shape, train_y.shape, test_X.shape, test_y.shape)
	return {'train_X': train_X,'train_y': train_y,'test_X': test_X,'test_y':test_y}


def make_model(path: str):
	"""
	Makes an LSTM model based on a dataframe holding some data from the leg table.
	Arguments:
		path: Path to a pickled dataframe holding Leg data
	Returns:
	    None
	"""
	data = load_data(path)
	train_X, train_y, test_X, test_y = data['train_X'], data['train_y'], data['test_X'], data['test_y']
	
	# design network
	model = Sequential()
	model.add(LSTM(50, input_shape=(train_X.shape[1], train_X.shape[2])))
	model.add(Dense(1))
	model.compile(loss='mae', optimizer='adam')
	# fit network
	history = model.fit(train_X, train_y, epochs=50, batch_size=72, validation_data=(test_X, test_y), verbose=2, shuffle=False)
	# Save model
	model.save('model-{}'.format(datetime.now().strftime('%d-%m-%Y--%H--%M')))
	# plot history
	pyplot.plot(history.history['loss'], label='train')
	pyplot.plot(history.history['val_loss'], label='test')
	pyplot.legend()
	pyplot.show()


def load_model():
	return keras.models.load_model('model-17-02-2018--12--00')


if __name__ == '__main__':
	#save('all.pkl', datetime(2018,1,17,0,0,0), datetime(2018, 1, 18, 0, 0, 0))
	#make_model('all.pkl')
	model = load_model()
	data = load_data('all.pkl')
	test_X, test_y = data['test_X'], data['test_y']
