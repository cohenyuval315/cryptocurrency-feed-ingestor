class BaseTradingStrategy:

    def __init__(self,
                 strategy_name: str,
                 strategy_desc: str,
                 symbols: list,
                 quantity,
                 exchange,
                 listener=None,
                 streams: list = None,
                 candle_intervals: list = None,
                 test=False,
                 write_to_file=False,
                 file_type="txt",
                 notify=False,
                 ask_permission=False) -> None:
        self.write_to_file = write_to_file
        self.notify = notify
        self.ask_permission = ask_permission
        self.streams = streams
        self.file_type = file_type
        self.exchange = exchange
        self.quantity = quantity
        self.symbols = symbols
        self.test = test
        self.candle_intervals = candle_intervals
        self.listener = listener
        if self.listener:
            self.listener_name = listener.__name__
        self.strategy_name = strategy_name
        self.strategy_desc = strategy_desc
        self.actions_taken = {}

    async def set_symbol(self, symbols: list):
        self.symbols = symbols

    async def set_streams(self, streams: list):
        self.streams = streams

    async def set_candle_intervals(self, candle_intervals: list):
        self.candle_intervals = candle_intervals
        if not candle_intervals:
            self.candle_intervals = ["1m"]

    async def set_quantity(self, quantity):
        self.quantity = quantity

    async def get_symbols(self):
        return self.symbols

    async def get_streams(self):
        return self.streams

    async def start(self):
        raise NotImplementedError

    async def process_data(self, msg):
        raise NotImplementedError

    async def prep(self):
        raise NotImplementedError

    # todo
    async def config(self):
        raise NotImplementedError
