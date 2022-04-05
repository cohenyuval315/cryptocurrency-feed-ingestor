# from tools import all
# logs
from typing import Type, Union

from client.exchange.exchange_model.exchange import RestExchange, Exchange


# how much should strat wait before handling data
class MaintenanceInterval:
    REAL_TIME = "0m"
    EVERY_1MINUTE = "1m"
    EVERY_3MINUTE = "3m"
    EVERY_5MINUTE = "5m"
    EVERY_15MINUTE = "15m"
    EVERY_30MINUTE = "30m"
    EVERY_1HOUR = "1h"
    EVERY_2HOUR = "2h"
    EVERY_4HOUR = "4h"
    EVERY_6HOUR = "6h"
    EVERY_8HOUR = "8h"
    EVERY_12HOUR = "12h"
    EVERY_1DAY = "1d"
    EVERY_3DAY = "3d"
    EVERY_1WEEK = "1w"
    EVERY_1MONTH = "1M"


class BaseStrategy:

    def __init__(self,
                 strategy_name: str,
                 strategy_desc: str,
                 symbols: list,
                 quantity,
                 exchange,
                 listener=None,
                 streams: list = None,
                 candle_intervals: list = None,
                 test=False,
                 write_to_file=False,
                 file_type="txt",
                 notify=False,
                 ask_permission=False) -> None:  # tool_list: list[str] = None
        self.order_condition = True
        self.api_condition = True
        self.write_to_file = write_to_file
        self.notify = notify
        self.ask_permission = ask_permission
        self.streams = streams
        self.file_type = file_type
        self.exchange = exchange
        self.quantity = quantity
        self.symbols = symbols
        self.test = test
        self.candle_intervals = candle_intervals
        self.listener = listener
        if self.listener:
            self.listener_name = listener.__name__
        # self.save_data = None
        self.strategy_name = strategy_name
        self.strategy_desc = strategy_desc
        self.actions_taken = {}

    async def set_symbol(self, symbols, streams):
        self.symbols = symbols
        self.streams = streams

    async def set_quantity(self, quantity):
        self.quantity = quantity

    async def get_symbols(self):
        return self.symbols

    async def get_streams(self):
        return self.streams

    async def start(self):
        raise NotImplementedError

    async def process_data(self, msg):
        raise NotImplementedError
