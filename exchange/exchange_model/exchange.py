import asyncio

class RestExchange:

    async def init_information(self):
        raise NotImplementedError

    async def spot_oco_order(self, **kwargs):
        raise NotImplementedError

    async def spot_order(self,**kwargs):
        raise NotImplementedError

    async def spot_cancel_order(self,  **kwargs):
        raise NotImplementedError

    async def get_order_book_snapshot(self, **kwargs):
        raise NotImplementedError

    async def get_all_order_books_best_tickers(self,  **kwargs):
        raise NotImplementedError

    async def get_all_symbols_prices(self, **kwargs):
        raise NotImplementedError

    async def get_all_symbols_info(self, **kwargs):
        raise NotImplementedError

    async def get_spot_symbols_names(self,**kwargs):
        raise NotImplementedError

    async def get_history_klines(self, **kwargs):
        raise NotImplementedError

    async def get_history_trades(self, **kwargs):
        raise NotImplementedError

    @classmethod
    async def _check_availability_status(cls,  **kwargs):
        raise NotImplementedError

    async def get_all_coins_info(self, **kwargs):
        raise NotImplementedError


class Exchange:

    # normalize msg data class

    async def set_time_settings(self, **kwargs):
        raise NotImplementedError

    def get_all_streams_kafka_topics(self):
        # """list of dict , each dict = {exchange: , symbol: , event: , interval: ,}"""
        raise NotImplementedError

    def get_name(self):
        raise NotImplementedError


    # @classmethod
    # def info(cls) -> Dict:
    #     """
    #     Return information about the Exchange for REST and Websocket data channels
    #     """
    #     symbols = cls.symbol_mapping()
    #     data = Symbols.get(cls.id)[1]
    #     data['symbols'] = list(symbols.keys())
    #     data['channels'] = {
    #         'rest': list(cls.rest_channels) if hasattr(cls, 'rest_channels') else [],
    #         'websocket': list(cls.websocket_channels.keys())
    #     }
    #     return data

async def main():
    pass

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
