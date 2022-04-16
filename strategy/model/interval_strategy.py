import asyncio
import datetime
from client.strategy.model.base_trading_strategy import BaseTradingStrategy
from client.file_handler import RestFileHandler
from client.util.time import str_to_time


class IntervalStrategy(BaseTradingStrategy):
    file_length_counter = 0

    def __init__(self,
                 strategy_name: str,
                 strategy_desc: str,
                 symbols: list,
                 quantity,
                 exchange,
                 # interval trading strategy extra arguments
                 interval: int,
                 interval_type: str,
                 read_saved_data=True,
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
        self.old_data = None
        self.ready_interval = self._set_interval(interval, interval_type)
        self.read_saved_data = read_saved_data
        self.write_to_file = write_to_file
        if self.write_to_file or self.read_saved_data:
            self.rfh = RestFileHandler(file_type=self.file_type)
            self.file_name = self.strategy_name + "_file"
            self.file_name_date = self.strategy_name + "_rerun_date"

    def _set_interval(self, interval: int, interval_type: str):
        interval_time = str_to_time(interval_type)
        if not interval_time:
            raise Exception("wrong interval type")
        self.ready_interval = interval * interval_time
        return self.ready_interval

    async def interval_data_request(self, *kwargs):
        raise NotImplementedError

    async def prep(self):
        # change as well
        print("starting ", self.strategy_name)
        if self.read_saved_data:
            date_to_run = await self.rfh.read_from_file(self.strategy_name, self.file_name_date)
            self.old_data = await self.rfh.read_dir(self.strategy_name, self.file_name, True)
            date = datetime.datetime.now()
            if date_to_run >= date:
                seconds_to_sleep = (date_to_run - date).total_seconds()
                await asyncio.sleep(seconds_to_sleep)


    async def start(self):
        try:
            while True:

                info = await self.interval_data_request()
                if info:
                    self.old_data.append(info)
                    if self.write_to_file:
                        time1 = datetime.datetime.today()
                        time2 = datetime.timedelta(self.ready_interval)
                        date_to_rerun = time1 + time2
                        await self.rfh.write_to_file(self.strategy_name, self.file_name_date, date_to_rerun, False,
                                                     truncate=True)
                        await self.rfh.write_to_file(self.strategy_name, self.file_name, info, True)
                await self.process_data(self.old_data)
                print("preparing wait ", self.strategy_name)
                await asyncio.sleep(self.ready_interval)

        except Exception as e:
            print("crash ", self.strategy_name)
            print(e)

    async def routine(self):
        info = await self.interval_data_request()
        if info:
            self.old_data.append(info)
            if self.write_to_file:
                time1 = datetime.datetime.today()
                time2 = datetime.timedelta(self.ready_interval)
                date_to_rerun = time1 + time2
                await self.rfh.write_to_file(self.strategy_name, self.file_name_date, date_to_rerun, False,
                                             truncate=True)
                await self.rfh.write_to_file(self.strategy_name, self.file_name, info, True)
        await self.process_data(self.old_data)
        print("preparing wait ", self.strategy_name)
        await asyncio.sleep(self.ready_interval)

    async def process_data(self, data):
        raise NotImplementedError


if __name__ == '__main__':
    pass
