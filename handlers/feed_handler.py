import asyncio
from typing import Type, Union

from client.exchange.binance_impl import Binance
from client.exchange.exchange_model.exchange import Exchange, RestExchange
from client.util.data_classes import ExchangeFeedKafka


class FeedHandler:

    def __init__(self, exchange) -> None:
        self.exchanges = []
        self.feeds_coroutines = None
        self.feeds_coroutines_gather = None
        self.running = False
        if not exchange:
            return
        if isinstance(exchange, list):
            self.exchanges.extend(exchange)
        else:
            self.exchanges.append(exchange)

    def get_exchanges_kafka_streams(self) -> list[ExchangeFeedKafka]:
        ready_list = []
        for exchange in self.exchanges:
            lst = exchange.get_all_streams_kafka_topics()  # list[ExchangeFeedKafka]
            ready_list.extend(lst)
        return ready_list

    async def start_feed(self):
        self.running = True
        tasks = []
        for exchange_feed in self.exchanges:
            tasks.append(exchange_feed.start())
        self.feeds_coroutines = tasks
        print("init feeds gathering")
        self.feeds_coroutines_gather = await asyncio.gather(*tasks, return_exceptions=True)

    async def stop_all(self):
        try:
            self.feeds_coroutines_gather.cancel()
            self.running = False
        except Exception as e:
            print(e)
