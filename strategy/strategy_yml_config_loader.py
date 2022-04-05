import yaml
import argparse


def load_general_strategies_config_info(info):
    try:
        return info['strategy']['quantity_in_usd'], info['is_bull_market'], info
    except Exception as e:
        print(e)
        exit("strategy-config-file:  error fetching")

# def sockets_string_builder(,coin_lst):
#     try:
#         return info['socket']['quantity_in_usd'], info['is_bull_market']
#     except Exception as e:
#         print(e)
#         exit("strategy-config-file:  error fetching")
