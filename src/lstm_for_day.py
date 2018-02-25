"""
Make an LSTM model based on a day's requests.

Most of the code is just lifted from
https://machinelearningmastery.com/multivariate-time-series-forecasting-lstms-keras/

"""
import os
import pandas as pd
import pickle as pkl
from datetime import datetime
from math import sqrt
from numpy import concatenate
from matplotlib import pyplot
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error
from keras.models import Sequential
import keras.models
from keras.layers import Dense
from keras.layers import LSTM

from leg import Leg


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
    query = session.query(Leg). \
        filter(Leg.request_time >= date_after). \
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
    df = pd.DataFrame(data)
    cols, names = list(), list()
    # input sequence (t-n, ... t-1)
    for i in range(n_in, 0, -1):
        cols.append(df.shift(i))
        names += [('var%d(t-%d)' % (j + 1, i)) for j in range(n_vars)]
    # forecast sequence (t, t+1, ... t+n)
    for i in range(0, n_out):
        cols.append(df.shift(-i))
        if i == 0:
            names += [('var%d(t)' % (j + 1)) for j in range(n_vars)]
        else:
            names += [('var%d(t+%d)' % (j + 1, i)) for j in range(n_vars)]
    # put it all together
    agg = pd.concat(cols, axis=1)
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

    # Move price to the end as it's what we're predicting
    cols = df.columns.tolist()
    cols = cols[1:] + cols[:1]
    df = df[cols]

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
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(values)
    print('Values shape: {}'.format(values.shape))
    print('df: {}'.format(df))
    reframed = series_to_supervised(scaled)
    print('Reframed shape: {}'.format(reframed.shape))

    # Need to drop columns we don't want to predict
    reframed.drop(reframed.columns[[6, 7, 8, 9, 10]], axis=1, inplace=True)

    # split into train and test sets
    values = reframed.values
    n_train = values.shape[0] - 1000
    train = values[:n_train, :]
    test = values[n_train:, :]
    # split into input and outputs
    train_X, train_y = train[:, :-1], train[:, -1]
    test_X, test_y = test[:, :-1], test[:, -1]
    # reshape input to be 3D [samples, timesteps, features]
    train_X = train_X.reshape((train_X.shape[0], 1, train_X.shape[1]))
    test_X = test_X.reshape((test_X.shape[0], 1, test_X.shape[1]))
    print(train_X.shape, train_y.shape, test_X.shape, test_y.shape)
    return {'train_X': train_X, 'train_y': train_y, 'test_X': test_X, 'test_y': test_y, 'scaler': scaler}


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
    history = model.fit(train_X, train_y, epochs=50, batch_size=72, validation_data=(test_X, test_y), verbose=2,
                        shuffle=False)
    # Save model
    save_to = 'model-{}'.format(datetime.now().strftime('%d-%m-%Y--%H--%M'))
    model.save(save_to)
    # plot history
    pyplot.plot(history.history['loss'], label='train')
    pyplot.plot(history.history['val_loss'], label='test')
    pyplot.legend()
    pyplot.show()
    return save_to


def invert_scaling(scaler, y, x):
    """
    Undoes the work of scaler so we can look at how the model is doing
    in the pre-feature-engineered problem space.

    Arguments:
        scaler: The scaler that squashed the values in the first place
        y: The column of (scaled) output values *from* the model
        x: Matrix of (munged) input data *to* the model

    Returns:
        y as it was before it got squashed by the scaler, that is,
        a column that when you apply scaler to it becomes y
    """
    x = x.reshape((x.shape[0], x.shape[2]))
    inv_y = concatenate((y, x[:, 1:]), axis=1)
    inv_y = scaler.inverse_transform(inv_y)
    return inv_y[:, 0]


def predict():
    """
    Works out the RMSE of the models predictions against reality in the
    test data.
    """
    model = keras.models.load_model(os.path.join(os.pardir, 'model-18-02-2018--21--45'))
    data = load_data(os.path.join(os.pardir, 'all.pkl'))

    # Make a prediction
    test_X, test_y = data['test_X'], data['test_y']
    scaler = data['scaler']
    yhat = model.predict(test_X)

    print('yhat shape: {}'.format(yhat.shape))
    print('y shape: {}'.format(test_y.shape))

    # Invert scaling for predicted
    inv_yhat = invert_scaling(scaler, yhat, test_X)

    # Invert scaling for actual
    test_y = test_y.reshape((len(test_y), 1))
    inv_y = invert_scaling(scaler, test_y, test_X)

    for i in range(50):
        print('Predicted: {}\tActual: {}\n'.format(inv_yhat[i], inv_y[i]))

    rmse = sqrt(mean_squared_error(inv_y, inv_yhat))
    print('Test RMSE: %.3f' % rmse)


if __name__ == '__main__':
    predict()
