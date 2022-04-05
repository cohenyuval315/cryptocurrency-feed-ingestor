import asyncio
import dataclasses

from client.strategy.model.base_strategy import BaseStrategy
from client.strategy.model.interval_strategy import IntervalStrategy
from client.strategy.model.real_time_strategy import RealTimeStrategy


class StrategyManager:
    REAL_TIME_STRATEGY: {}
    INTERVAL_STRATEGY: {}

    def __init__(self, realtime_delay, interval_delay, config=None):
        self.realtime_delay = realtime_delay
        self.interval_delay = interval_delay
        self.config = config if config else "Nada ASDAS"

    def add_strategy(self, strategy: BaseStrategy):
        if isinstance(strategy, RealTimeStrategy):
            self.REAL_TIME_STRATEGY[strategy.strategy_name] = strategy
        if isinstance(strategy, IntervalStrategy):
            self.INTERVAL_STRATEGY[strategy.strategy_name] = strategy

    async def run_all(self):
        await asyncio.gather(self.run_realtime(),self.run_interval())

    async def run_realtime(self):
        s1 = self.REAL_TIME_STRATEGY
        tasks = []
        await asyncio.sleep(self.realtime_delay)
        for s in s1.values():
            tasks.append(s.start())
            print("loading", s.strategy_name)
        await asyncio.gather(*tasks, return_exceptions=True)

    async def run_interval(self):
        s2 = self.INTERVAL_STRATEGY
        tasks = []
        await asyncio.sleep(self.interval_delay)
        for s in s2.values():
            tasks.append(s.start())
            print("loading", s.strategy_name)
        await asyncio.gather(*tasks, return_exceptions=True)

    # async def get_algo_trading_symbols(self):
    #     symbols = []
    #     for s in self.realtime_delay:
    #         sym_s = await s.get_symbols()
    #         symbols += sym_s
    #     return symbols
    # async def get_interval_trading_symbols(self):
    #     symbols = []
    #     for s in self.INTERVAL_STRATEGY.items():
