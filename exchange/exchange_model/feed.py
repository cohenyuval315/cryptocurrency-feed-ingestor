from abc import ABC
from client.exchange.exchange_model.exchange import Exchange


class Feed(Exchange, ABC):

    #  candle_interval = '1m', timeout = 120, timeout_interval = 30, retries = 10 subscription=None,
    #   delay_start=0, callbacks=None, exceptions=None,
    # self.previous_book = defaultdict(dict)  # no idea
    # self._feed_config = defaultdict(list)  # no idea
    # self._sequence_no = {}
    # self.delay_start = delay_start
    # self.subscription = subscription
    # self.exceptions = exceptions
    # self.callbacks = callbacks
    # self.retries = retries
    # self.timeout_interval = timeout_interval
    # self.timeout = timeout
    # self.requires_authentication = False
    # self.log_message_on_error = log_message_on_error
    # self.running = None

    def add_feed(self, symbols, streams: list, candle_intervals: list = None, max_depth=0):
        raise NotImplementedError

    async def start(self):
        raise NotImplementedError

    async def _user_feed(self, *kwargs):
        raise NotImplementedError

    async def _feed(self, *kwargs):
        raise NotImplementedError

    async def _process_msg(self, *kwargs):
        raise NotImplementedError

    async def stop(self):
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError
