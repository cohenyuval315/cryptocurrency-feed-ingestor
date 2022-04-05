import asyncio
from typing import Type

from binance import AsyncClient, BinanceSocketManager

from client.exchange.binance_impl import Binance
from client.exchange.exchange_model.exchange import Exchange, RestExchange
from client.strategy.model.interval_strategy import IntervalStrategy


class DCA(IntervalStrategy):

    # remove streams
    def __init__(self,
                 strategy_name: str,
                 strategy_desc: str,
                 symbols: list,
                 quantity,
                 exchange,
                 interval: int,
                 interval_type: str,
                 read_saved_data=True,
                 data_from_start_time=None,
                 data_until_end_time=None,
                 listener=None,
                 streams: list = None,
                 candle_intervals: list = None,
                 test=False,
                 write_to_file=False,
                 file_type="txt",
                 notify=False,
                 ask_permission=False
                 ):
        super().__init__(strategy_name, strategy_desc, symbols, quantity, exchange, interval, interval_type,
                         read_saved_data, data_from_start_time, data_until_end_time, listener, streams,
                         candle_intervals,
                         test, write_to_file, file_type, notify, ask_permission)

    async def interval_data_request(self, *kwargs):
        return None

    # this msg done in the intervals arguments automatically
    async def process_data(self, data):
        precentage = 10 / 100
        partition = self.quantity * precentage
        btcusdt = self.symbols[0]
        print("ordering")
        # NO CLIENT I FORGOT I NEED TO DO THAT SOMEHOW

        await self.exchange.spot_order(symbol=btcusdt, order_type=Binance.ORDER_TYPE_MARKET,
                                       side="BUY", quantity=partition, test=True)
        print("done ordering")
        # await self.exchange.spot_order(self=self.exchange,symbol=btcusdt, order_type=Binance.ORDER_TYPE_MARKET,
        #                          side="BUY", quoteOrderQty=partition, test=True)
