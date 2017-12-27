import downloader
import pprint
import pickle as pkl
from datetime import datetime


def load_example_leg():
    with open('../data/26-12-17_12_16.pkl', 'rb') as f:
        pickle = pkl.load(f)
    return pickle[0], next(iter(pickle[1].values()))


def pull_numbers(time, leg):
    dt = datetime.strptime(time, "%d-%m-%y_%H_%M")
    print("Time of request: {}".format(dt))
    print(leg['price']['totalPriceAsDecimal'])
    print(leg['carrierSummary'])
    print(leg['stops'])


def create_dev_aids():
    '''
    Writes the key/value structure of a 'leg' to some text files in the ../data folder to make it a bit clearer
    what's going on.
    '''
    first_leg = load_example_leg()
    with open('../data/key_structure.txt', 'w') as f:
        f.write(visualise(first_leg, 1))
    with open('../data/value_structure.txt', 'w') as f:
        pprint.pprint(first_leg, stream=f)


def visualise(dict_of_dicts: dict, n_nestings: int) -> str:
    result = ''
    for key, value in dict_of_dicts.items():
        result += key + ','
        if isinstance(value, dict): 
            result += '\n' + ('\t' * n_nestings) + '[' + visualise(value, n_nestings + 1) + ']\n'
        else: 
            result += '\n' + ('\t' * (n_nestings - 1))
    return result


if __name__ == '__main__':
    eg = load_example_leg()
    pull_numbers(eg[0], eg[1])