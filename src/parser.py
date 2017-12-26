import downloader
import pprint

def create_dev_aids():
    '''
    Writes the key/value structure of a 'leg' to some text files in the ../data folder to make it a bit clearer
    what's going on.
    '''
    json = downloader.download()[1]
    first_leg = next(iter(json.values()))
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
    create_dev_aids()