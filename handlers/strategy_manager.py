import asyncio
import dataclasses

from client.strategy.model.base_trading_strategy import BaseTradingStrategy
from client.strategy.model.interval_strategy import IntervalStrategy
from client.strategy.model.real_time_strategy import RealTimeStrategy


class StrategyManager:
    real_time_trading_strategies: {}
    interval_trading_strategies: {}

    def __init__(self, realtime_delay, interval_delay, config=None):
        self.realtime_delay = realtime_delay
        self.interval_delay = interval_delay
        self.config = config if config else "Nada ASDAS"

    def add_strategy(self, strategy: BaseTradingStrategy):
        if isinstance(strategy, RealTimeStrategy):
            self.real_time_trading_strategies[strategy.strategy_name] = strategy
        if isinstance(strategy, IntervalStrategy):
            self.interval_trading_strategies[strategy.strategy_name] = strategy

    async def run_all(self):
        await asyncio.gather(self.run_realtime(),self.run_interval())

    async def run_realtime(self):
        s1 = self.real_time_trading_strategies
        tasks = []
        await asyncio.sleep(self.realtime_delay)
        for s in s1.values():
            tasks.append(s.start())
            print("loading", s.strategy_name)
        await asyncio.gather(*tasks, return_exceptions=True)

    async def run_interval(self):
        s2 = self.interval_trading_strategies
        tasks = []
        await asyncio.sleep(self.interval_delay)
        for s in s2.values():
            tasks.append(s.start())
            print("loading", s.strategy_name)
        await asyncio.gather(*tasks, return_exceptions=True)

    async def config_realtime(self,name):
        pass

    # async def run_a(self):todo
    #     s2 = self.interval_trading_strategies
    #     tasks = []
    #     await asyncio.sleep(self.interval_delay)
    #     for s in s2.values():
    #         tasks.append(s.start())
    #         print("loading", s.strategy_name)
    #         # s.prep()
    #     await asyncio.gather(*tasks, return_exceptions=True)
    #     all tasks = s.rountines
    #     while True:
    #         asyncio.create_task(alltasks)
    #         s.routine

    async def config_interval(self,name):
        pass

    # async def get_algo_trading_symbols(self):
    #     symbols = []
    #     for s in self.realtime_delay:
    #         sym_s = await s.get_symbols()
    #         symbols += sym_s
    #     return symbols
    # async def get_interval_trading_symbols(self):
    #     symbols = []
    #     for s in self.INTERVAL_STRATEGY.items():
