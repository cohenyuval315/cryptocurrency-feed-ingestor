from abc import ABC
from client.exchange.exchange_model.exchange import Exchange


class Feed(Exchange, ABC):

    def add_feed(self, symbols, streams: list, candle_intervals: list = None, max_depth=0):
        raise NotImplementedError

    async def normalize_msg(self, *kwargs):
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError
