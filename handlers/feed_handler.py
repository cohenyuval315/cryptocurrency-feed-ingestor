import asyncio
import time
from client.util.data_classes import ExchangeFeed


class FeedHandler:

    def __init__(self, exchange, callback=None) -> None:
        self.callback = callback
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

    def get_exchanges_feeds(self) -> list[ExchangeFeed]:
        ready_list = []
        for exchange in self.exchanges:
            lst = exchange.get_all_exchange_feed()  # list[ExchangeFeed]
            ready_list.extend(lst)
        return ready_list

    async def start_feed(self):
        tasks = []
        for exchange in self.exchanges:
            tasks.append(self.feed(exchange, await exchange.get_feed_socket_object()))
            for key, val in exchange.get_streams().items():
                if "user" in key:
                    tasks.append(self.feed(exchange, await exchange.get_user_socket_object()))

        self.running = True
        self.feeds_coroutines_gather = await asyncio.gather(*tasks, return_exceptions=True)

    async def feed(self, exchange, socket_obj):
        await asyncio.sleep(exchange.get_delay_start())
        feed_start_time = time.time()
        async with socket_obj as stream:
            while True:
                res = await stream.recv()
                msg = await exchange.normalize_msg(res)
                if self.callback:
                    asyncio.create_task(self.callback(msg))
                feed_since_start = time.time() - feed_start_time
                if feed_since_start >= exchange.get_timeout():
                    break

    async def stop_all(self):
        try:
            self.feeds_coroutines_gather.cancel()
            self.running = False
        except Exception as e:
            print(e)
