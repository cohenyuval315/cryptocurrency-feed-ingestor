from sys import exit

import yaml


def load_correct_key_info(info):
    try:
        return info['product']['binance_access_key'], info['product']['binance_secret_key']
    except Exception as e:
        print("error fetching keys")
        print(e)

def load_config(file):
    try:
        with open(file) as file:
            return yaml.load(file, Loader=yaml.FullLoader)
    except FileNotFoundError:
        exit(f'Could not find {file}')
    except Exception as e:
        exit(f'Encountered exception...\n {e}')
