import downloader

def parse():
    json = downloader.download()[1]
    first_leg = next(iter(json.values()))
    with open('../data/json_structure.txt', 'w') as f:
        f.write(visualise(first_leg, 1))

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
    parse()