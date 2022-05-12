import asyncio


class RestExchange:

    async def init_information(self):
        raise NotImplementedError

    async def spot_oco_order(self, **kwargs):
        raise NotImplementedError

    async def spot_order(self, **kwargs):
        raise NotImplementedError

    async def spot_cancel_order(self, **kwargs):
        raise NotImplementedError

    async def get_order_book_snapshot(self, **kwargs):
        raise NotImplementedError

    async def get_all_order_books_best_tickers(self, **kwargs):
        raise NotImplementedError

    async def get_all_symbols_prices(self, **kwargs):
        raise NotImplementedError

    async def get_all_symbols_info(self, **kwargs):
        raise NotImplementedError

    async def get_symbol_info(self, **kwargs):
        raise NotImplementedError

    async def get_spot_symbols_names(self, **kwargs):
        raise NotImplementedError

    async def get_history_klines(self, **kwargs):
        raise NotImplementedError

    async def get_history_trades(self, **kwargs):
        raise NotImplementedError

    async def _check_availability_status(self, **kwargs):
        raise NotImplementedError

    async def get_all_coins_info(self, **kwargs):
        raise NotImplementedError


class Exchange:
    USER = "user"

    def set_timeout(self, **kwargs):
        raise NotImplementedError

    def set_delay_start(self, **kwargs):
        raise NotImplementedError

    def get_all_exchange_feed(self):
        raise NotImplementedError

    def get_name(self) -> str:
        raise NotImplementedError

    def get_feed_socket_object(self):
        raise NotImplementedError

    def get_user_socket_object(self):
        raise NotImplementedError

    def get_timeout(self):
        raise NotImplementedError

    def get_streams(self) -> dict:
        raise NotImplementedError

    def get_delay_start(self):
        raise NotImplementedError

    async def normalize_msg(self, msg):
        raise NotImplementedError

async def main():
    pass


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
