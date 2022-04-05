import asyncio
from abc import ABC
from typing import Type

from client.backend.kafka_impl import get_exchange_kafka_topics
from client.file_handler import KafkaFileConsumer
from client.exchange.exchange_model.exchange import Exchange
from client.strategy.model.base_strategy import BaseStrategy


# ttlcache
class RealTimeStrategy(BaseStrategy):

    def __init__(self,
                 strategy_name: str,
                 strategy_desc: str,
                 symbols: list,
                 quantity,
                 exchange: Type[Exchange],
                 listener,
                 streams: list,
                 candle_intervals: list = None,
                 test=False,
                 write_to_file=False,
                 file_type="txt",
                 notify=None,
                 ask_permission=None,
                 cache=True):
        super().__init__(strategy_name, strategy_desc, symbols, quantity, exchange, listener, streams, candle_intervals,
                         test, write_to_file, file_type, notify, ask_permission)

        if candle_intervals:
            if "kline" not in streams:
                streams.append("kline")
        if self.listener_name == "KafkaFeedConsumer":
            topics = get_exchange_kafka_topics(exchange, symbols, streams, candle_intervals)
            self.listener = listener().subscribe_topics(topics=topics)
        if self.write_to_file:
            self.kfh = KafkaFileConsumer(file_type=self.file_type)

        self.cache = cache
        if self.cache:
            pass
        # TODO

    async def start(self):
        try:
            if self.listener_name == "KafkaFeedConsumer":
                self.listener.read(self.prepare, True)
        except Exception as e:
            print(e)
        finally:
            if self.write_to_file:
                # todo
                pass

    async def prepare(self, msg):
        await self.process_data(msg)
        # save to cache

        # maybe will hurt performance
        # if self.write_to_file:
        #     self.kfh.consume_to_file()
        #     pass
        # todo

    async def process_data(self, msg):
        raise NotImplementedError
