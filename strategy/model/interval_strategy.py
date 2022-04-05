import asyncio
import datetime
import os
from typing import Type, Union

from client.backend.kafka_impl import KafkaFeedConsumer
from client.exchange.exchange_model.exchange import Exchange, RestExchange

from client.strategy.model.base_strategy import BaseStrategy
from client.file_handler import FileHandler, RestFileHandler
from client.util.time import str_to_time


class IntervalStrategy(BaseStrategy):
    file_length_counter = 0

    def __init__(self,
                 strategy_name: str,
                 strategy_desc: str,
                 symbols: list,
                 quantity,
                 exchange,
                 # interval strat extra arguments
                 interval: int,
                 interval_type: str,
                 read_saved_data=True,
                 data_from_start_time=None,
                 data_until_end_time=None,
                 # <-->
                 listener=None,
                 streams: list = None,
                 candle_intervals: list = None,
                 test=False,
                 write_to_file=False,
                 file_type="txt",
                 notify=False,
                 ask_permission=False
                 ):

        super().__init__(strategy_name, strategy_desc, symbols, quantity, exchange, listener, streams, candle_intervals,
                         test, write_to_file, file_type, notify, ask_permission)
        self.data_from_start_time = data_from_start_time
        self.data_until_end_time = data_until_end_time
        self.ready_interval = self._set_interval(interval, interval_type)
        self.read_saved_data = read_saved_data

        # argument file handler?
        self.rfh = RestFileHandler(file_type=self.file_type)

    def _set_interval(self, interval: int, interval_type: str):
        interval_time = str_to_time(interval_type)
        if not interval_time:
            raise Exception("wrong interval type")
        return interval * interval_time

    async def interval_data_request(self, *kwargs):
        # maybe data class
        raise NotImplementedError

    async def start(self):
        all_data = []
        file_name = "interval"
        if self.read_saved_data:
            all_data = await self.rfh.read_dir(self.strategy_name,file_name,True)

        while True:
            print("starting ", self.strategy_name)
            try:
                info = await self.interval_data_request()
                if info:
                    all_data.append(info)
                    if self.write_to_file:
                        await self.rfh.write_to_file(self.strategy_name, file_name, info,True)
                await self.process_data(all_data)
                print("preparing wait ", self.strategy_name)
                await asyncio.sleep(self.ready_interval)
            except Exception as e:
                print("crash ", self.strategy_name)
                print(e)

    # PREP BEFORE FILE WRITING NEED TO IMP #todo

    async def process_data(self, data):
        # trading strategy implement
        # pandas?
        raise NotImplementedError


if __name__ == '__main__':
    rfh = RestFileHandler()
    rfh.write_to_file("name", "interval", "bla1",True)
    rfh.write_to_file("name", "interval", "bla2",True)
    rfh.write_to_file("name", "interval", "bla3",True)
    rfh.write_to_file("name", "interval", "bla4",True)
    t = rfh.read_dir("name","interval",True)
    print(t)
