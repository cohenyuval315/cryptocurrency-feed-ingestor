
import datetime
from binance import AsyncClient, BinanceSocketManager, Client
from binance.enums import HistoricalKlinesType
from client.exchange.exchange_model.exchange_helpers import limit_num_api
from client.exchange.exchange_model.feed import Feed
from client.exchange.exchange_model.exchange import RestExchange
from client.util.data_classes import RateLimit, ExchangeFeed


class BinanceRest(RestExchange):
    BINANCE = "binance"
    SPOT = "SPOT"
    MARGIN = "MARGIN"
    FUTURE = "FUTURES"

    # <--- INIT --->
    def __init__(self, client: AsyncClient):
        # MAYBE put them in REST-EXCHANGE class todo
        self.client = client
        self.exchange_info = None
        self.valid_symbols = None
        self.limit_request_num = None
        self.limit_order_num: tuple = (0, 0)
        self.order_limits = None
        self.api_limits = None
        self.date_time_for_sec_limits = datetime.datetime.now()
        self.date_time_for_day_limits = datetime.datetime.now()
        self.coins_info = None

    def init_information(self, *kwargs):
        c = Client()  # todo clean
        self.exchange_info = c.get_exchange_info()
        self.valid_symbols = [symbol["symbol"] for symbol in self.exchange_info["symbols"] if
                              symbol["isSpotTradingAllowed"]]
        status = c.get_system_status()
        if status["status"] > 0:
            print(self.BINANCE, " ", status["msg"])
            raise Exception("binance server offline")
        c.close_connection()
        self.limit_request_num = 13
        self.limit_order_num = (0, 0)
        rl = self.exchange_info["rateLimits"]
        rtemp = rl[1]
        limit_type = rtemp["rateLimitType"].lower()
        interval = rtemp["interval"].lower()
        limit = rtemp["limit"]
        interval_num = rtemp["intervalNum"]
        if interval_num:
            order_limit_1 = RateLimit(limit_type, interval, interval_num, limit)
        else:
            order_limit_1 = RateLimit(limit_type, interval, 1, limit)

        rtemp = rl[2]
        limit_type = rtemp["rateLimitType"].lower()
        interval = rtemp["interval"].lower()
        limit = rtemp["limit"]
        interval_num = rtemp["intervalNum"]
        if interval_num:
            order_limit_2 = RateLimit(limit_type, interval, interval_num, limit)
        else:
            order_limit_2 = RateLimit(limit_type, interval, 1, limit)

        rtemp = rl[0]
        limit_type = rtemp["rateLimitType"].lower()
        interval = rtemp["interval"].lower()
        limit = rtemp["limit"]
        interval_num = rtemp["intervalNum"]
        if interval_num:
            api_limit_1 = RateLimit(limit_type, interval, interval_num, limit)
        else:
            api_limit_1 = RateLimit(limit_type, interval, 1, limit)

        # redundant
        # rtemp = rl[3]
        self.order_limits = [order_limit_1, order_limit_2]
        self.api_limits = api_limit_1

    async def get_client(self):
        return self.client

    @limit_num_api(1)
    async def _check_availability_status(self, **kwargs):
        """check if server online"""
        status = await self.client.get_system_status()
        if status["status"] > 0:
            print(self.BINANCE, " ", status["msg"])
            return False
        return True

    async def get_spot_symbols_names(self, **kwargs):
        all_symbols = await self.get_all_symbols_info()
        lst = [symbol["symbol"] for symbol in all_symbols if symbol["isSpotTradingAllowed"]]
        return lst

    # <--- INFO --->
    @limit_num_api(2)
    async def get_all_symbols_prices(self):
        """all current symbols base/quote

        return example:
        [
          {
            "symbol": "ETHBTC",
            "price": "0.07053000"
          },
          .
          .
          .
        ]
        """
        info = await self.client.get_all_tickers()
        return info

    async def get_all_symbols_info(self, **kwargs):
        """Return rate limits and list of symbols

        return example:
           {
            "timezone": "UTC",
            "serverTime": 1508631584636,
            "rateLimits": [
                {
                    "rateLimitType": "REQUESTS",
                    "interval": "MINUTE",
                    "limit": 1200
                },
                {
                    "rateLimitType": "ORDERS",
                    "interval": "SECOND",
                    "limit": 10
                },
                {
                    "rateLimitType": "ORDERS",
                    "interval": "DAY",
                    "limit": 100000
                }
            ],
            "exchangeFilters": [],
            "symbols": [
                {
                    "symbol": "ETHBTC",
                    "status": "TRADING",
                    "baseAsset": "ETH",
                    "baseAssetPrecision": 8,
                    "quoteAsset": "BTC",
                    "quotePrecision": 8,
                    "orderTypes": ["LIMIT", "MARKET"],
                    "icebergAllowed": false,
                    "filters": [
                        {
                            "filterType": "PRICE_FILTER",
                            "minPrice": "0.00000100",
                            "maxPrice": "100000.00000000",
                            "tickSize": "0.00000100"
                        }, {
                            "filterType": "LOT_SIZE",
                            "minQty": "0.00100000",
                            "maxQty": "100000.00000000",
                            "stepSize": "0.00100000"
                        }, {
                            "filterType": "MIN_NOTIONAL",
                            "minNotional": "0.00100000"
                        }
                    ]
                }
            ]
        }
        """
        if not self.client:
            return
        if not self.exchange_info:
            return
        return self.exchange_info["symbols"]

    @limit_num_api(10)
    async def get_exchange_info(self, **kwargs):
        binance_info = await self.client.get_exchange_info()
        return binance_info

    @limit_num_api(5)
    async def get_history_klines(self, symbol, interval, start_str, end_str=None, limit=500,
                                 klines_type=HistoricalKlinesType.SPOT):
        """Get Historical Klines from Binance

        :param symbol: Name of symbol pair e.g BNBBTC
        :type symbol: str
        :param interval: Binance Kline interval
        :type interval: str
        :param start_str: Start date string in UTC format or timestamp in milliseconds
        :type start_str: str|int
        :param end_str: optional - end date string in UTC format or timestamp in milliseconds (default will fetch everything up to now)
        :type end_str: str|int
        :param limit: Default 500; max 1000.
        :type limit: int
        :param klines_type: Historical klines type: SPOT or FUTURES
        :type klines_type: HistoricalKlinesType

        :return: list of OHLCV values
        return example:
            [
              [
                1499040000000,      // Open time
                "0.01634790",       // Open
                "0.80000000",       // High
                "0.01575800",       // Low
                "0.01577100",       // Close
                "148976.11427815",  // Volume
                1499644799999,      // Close time
                "2434.19055334",    // Quote asset volume
                308,                // Number of trades
                "1756.87402397",    // Taker buy base asset volume
                "28.46694368",      // Taker buy quote asset volume
                "17928899.62484339" // Ignore.
              ]
            ]
        """
        info = await self.client.get_historical_klines(symbol, interval, start_str, end_str=end_str, limit=limit,
                                                       klines_type=klines_type)
        return info

    @limit_num_api(5)
    async def get_history_trades(self, symbol: str, limit: int = None, fromId: str = None):
        """get recent trades for symbol default 500 max 1000 or from last order id

        :param symbol: required
        :type symbol: str
        :param limit:  Default 500; max 1000.
        :type limit: int
        :param fromId:  TradeId to fetch from. Default gets most recent trades.
        :type fromId: str
        return example:
            [
                {
                "id": 787260277,
                "price": "3004.30000000",
                "qty": "0.00760000",
                "quoteQty": "22.83268000",
                "time": 1647978214745,
                "isBuyerMaker": false,
                "isBestMatch": true
                },
                .
                .
                .
            ]
        """
        info = await self.client.get_historical_trades(symbol=symbol, limit=limit, fromId=fromId)
        return info

    @limit_num_api(10)
    async def get_all_coins_info(self):
        """return all coins info

        return example:
        [
            {
                "coin": "COTI",
                "depositAllEnable": true,
                "withdrawAllEnable": true,
                "name": "COTI",
                "free": "0",
                "locked": "0",
                "freeze": "0",
                "withdrawing": "0",
                "ipoing": "0",
                "ipoable": "0",
                "storage": "0",
                "isLegalMoney": false,
                "trading": true,
                "networkList":
                [
                  {
                    "network": "BNB",
                    "coin": "COTI",
                    "withdrawIntegerMultiple": "0.00000001",
                    "isDefault": false,
                    "depositEnable": true,
                    "withdrawEnable": true,
                    "depositDesc": "",
                    "withdrawDesc": "",
                    "specialTips": "Please enter both MEMO and Address data, which are required to deposit COTI BEP2 tokens to your Binance account.",
                    "name": "BNB Beacon Chain (BEP2)",
                    "resetAddressStatus": false,
                    "addressRegex": "^(bnb1)[0-9a-z]{38}$",
                    "addressRule": "",
                    "memoRegex": "^[0-9A-Za-z\\-_]{1,120}$",
                    "withdrawFee": "0.93",
                    "withdrawMin": "1.86",
                    "withdrawMax": "10000000000",
                    "minConfirm": 1,
                    "unLockConfirm": 0,
                    "sameAddress": true
                  },
                  {
                    "network": "BSC",
                    "coin": "COTI",
                    "withdrawIntegerMultiple": "0.00000001",
                    "isDefault": false,
                    "depositEnable": true,
                    "withdrawEnable": true,
                    "depositDesc": "",
                    "withdrawDesc": "",
                    "specialTips": "",
                    "specialWithdrawTips": "The network you have selected is BSC. Please ensure that the withdrawal address supports the Binance Smart Chain network. You will lose your assets if the chosen platform does not support retrievals.",
                    "name": "BNB Smart Chain (BEP20)",
                    "resetAddressStatus": false,
                    "addressRegex": "^(0x)[0-9A-Fa-f]{40}$",
                    "addressRule": "",
                    "memoRegex": "",
                    "withdrawFee": "0.93",
                    "withdrawMin": "1.86",
                    "withdrawMax": "10000000000",
                    "minConfirm": 15,
                    "unLockConfirm": 0,
                    "sameAddress": false
                  },
                  {
                    "network": "ETH",
                    "coin": "COTI",
                    "withdrawIntegerMultiple": "0.00000001",
                    "isDefault": true,
                    "depositEnable": true,
                    "withdrawEnable": true,
                    "depositDesc": "",
                    "withdrawDesc": "",
                    "specialTips": "",
                    "name": "Ethereum (ERC20)",
                    "resetAddressStatus": false,
                    "addressRegex": "^(0x)[0-9A-Fa-f]{40}$",
                    "addressRule": "",
                    "memoRegex": "",
                    "withdrawFee": "136",
                    "withdrawMin": "272",
                    "withdrawMax": "10000000000",
                    "minConfirm": 12,
                    "unLockConfirm": 0,
                    "sameAddress": false
                  }
                ]
            },
            .
            .
            .
        ]

        """
        info = await self.client.get_all_coins_info()
        return info

    # <--- ACCOUNT --->
    @limit_num_api(10)
    async def get_account(self, **kwargs):
        res = await self.client.get_account()
        return res

    @limit_num_api(10)
    async def get_account_coin_balance(self, coin):
        bal = await self.client.get_asset_balance(coin)
        return bal

    @limit_num_api(1)
    async def coins_transportation_details(self, **kwargs):
        details = await self.client.get_asset_details()
        return details

    @limit_num_api(1)
    async def get_account_permissions(self, **kwargs):
        res = await self.client.get_account_api_permissions()
        return res

    @limit_num_api(10)
    async def get_account_orders(self, **kwargs):
        """Get all account orders; active, canceled, or filled."""
        res = await self.client.get_all_orders()
        return res

    @limit_num_api(1)
    async def get_account_api_trading_status(self, **kwargs):
        res = await self.client.get_account_api_trading_status()
        return res

    @limit_num_api(1)
    async def get_account_status(self, **kwargs):
        res = await self.client.get_account_status()
        return res

    @limit_num_api(2400)
    async def get_account_snapshot(self, **kwargs):
        acc = await self.client.get_account_snapshot()
        return acc

    @limit_num_api(10)
    async def get_number_of_running_orders(self, symbol=None):
        if symbol:
            orders = await self.client.get_open_orders(symbol=symbol)
            return orders, 3
        else:
            orders = await self.client.get_open_orders()
            return orders, 40

    # <--- ACTIONS -->
    @limit_num_api(4, True)
    async def spot_oco_order(self, symbol: str, side: str, stopPrice, quantity: float = None, price: str = None
                             , timeInForce: str = None, stopLimitPrice: str = None, stopIcebergQty=None,
                             newOrderRespType: str = None, recvWindow: int = None, listClientOrderId: str = None,
                             limitClientOrderId: str = None, stopClientOrderId=None, test=False):
        """
        :param symbol: required
        :type symbol: str
        :param listClientOrderId: A unique id for the list order. Automatically generated if not sent. also for cancel
        :type listClientOrderId: str
        :param side: required
        :type side: str
        :param quantity: required
        :type quantity: decimal
        :param limitClientOrderId: A unique id for the limit order. Automatically generated if not sent.
        :type limitClientOrderId: str
        :param price: required - price you want to sell or buy if reached
        :type price: str
        :param stopClientOrderId: A unique id for the stop order. Automatically generated if not sent.
        :type stopClientOrderId: str
        :param stopPrice: required -trigger the stop limit price
        :type stopPrice: str
        :param stopLimitPrice: If provided, stopLimitTimeInForce is required.
        :type stopLimitPrice: str
        :param stopIcebergQty: Used with STOP_LOSS_LIMIT leg to make an iceberg order.
        :type stopIcebergQty: decimal
        :param timeInForce: Valid values are GTC/FOK/IOC.
        :type timeInForce: str
        :param newOrderRespType: Set the response JSON. ACK, RESULT, or FULL; default: RESULT.
        :type newOrderRespType: str
        :param recvWindow: the number of milliseconds the request is valid for
        :type recvWindow: int
        """
        # if one order executes, then the other order is automatically canceled
        # Price Restrictions:
        #   SELL: Limit Price > Last Price > Stop Price
        #   BUY: Limit Price < Last Price < Stop Price
        # Quantity Restrictions:
        #   Both legs must have the same quantity
        #   ICEBERG quantities however do not have to be the same.
        # Order Rate Limit
        #   OCO counts as 2 orders against the order rate limit.

        if not test:
            await self.client.create_oco_order(symbol=symbol,
                                               listClientOrderId=listClientOrderId,
                                               side=side, quantity=quantity,
                                               limitClientOrderId=limitClientOrderId, price=price,
                                               stopClientOrderId=stopClientOrderId, stopPrice=stopPrice,
                                               stopLimitPrice=stopLimitPrice
                                               , stopIcebergQty=stopIcebergQty,
                                               recvWindow=recvWindow, timeInForce=timeInForce,
                                               newOrderRespType=newOrderRespType)
            return

    @limit_num_api(2, True)
    async def spot_order(self, symbol: str, order_type: str, side: str, quantity: float = None, price: str = None,
                         stopPrice: str = None, timeInForce: str = None, quoteOrderQty=None, iceberqQty: float = None,
                         newOrderRespType: str = None, recvWindow: int = None, newClientOrderId: str = None,
                         test: bool = False):
        """
        :param symbol: required
        :type symbol: str
        :param order_type: required
        :type order_type: str
        :param side: required, BUY or SELL
        :type side: str
        :param quantity: required, unless MARKET order with quoteOrderQty
        :type quantity: decimal
        :param price: required if LIMIT type order
        :type price: str
        :param stopPrice: required if LIMIT type order
        :type stopPrice: str
        :param timeInForce: required if LIMIT type order
        :type timeInForce: str
        :param quoteOrderQty: required if MARKET order, Example on ETHUSDT , 100 quoteOrderQty = 100 USDT
        :type quoteOrderQty: decimal
        :param iceberqQty: Used with iceberg orders,for big orders
        :type iceberqQty: decimal
        :param newClientOrderId: A unique id for the order. Automatically generated if not sent.
        :type newClientOrderId: str
        :param newOrderRespType: Set the response JSON. ACK, RESULT, or FULL; default: RESULT.
        :type newOrderRespType: str
        :param recvWindow: The number of milliseconds the request is valid for ,must be< 60,000
        :type recvWindow: int
        :param test: default False
        :type test: bool
        """
        if test:
            test = await self.client.create_test_order(symbol=symbol, side=side, timeInForce=timeInForce,
                                                       type=order_type,
                                                       recvWindow=recvWindow, stopPrice=stopPrice, price=price,
                                                       quantity=quantity,
                                                       quoteOrderQty=quoteOrderQty)  # :param symbol: required
            return test

        else:
            order = await self.client.create_order(symbol=symbol, side=side, timeInForce=timeInForce, type=order_type,
                                                   recvWindow=recvWindow, stopPrice=stopPrice, price=price,
                                                   quantity=quantity,
                                                   iceberqQty=iceberqQty, newOrderRespType=newOrderRespType,
                                                   newClientOrderId=newClientOrderId,
                                                   quoteOrderQty=quoteOrderQty)
            return order

        # self.client.create_order()
        # self.client.cancel_order()

    @limit_num_api(1)
    async def spot_cancel_order(self, symbol: str, orderId: str, recvWindow: int = None):
        """
        :param symbol: required
        :type symbol: str
        :param orderId: required
        :type symbol: str
        :param recvWindow:
        :type recvWindow: int
        :return:
        """
        cancel_oco = await self.client.cancel_order(symbol=symbol, orderId=orderId, recvWindow=recvWindow)
        return cancel_oco

    # <--- ORDER BOOK ---> /!\ UNDER CONSTRUCTION /!\
    # need trying
    # TODO
    # limit : weight
    # 1-100  	1
    # 101-500	5
    # 501-1000	10
    # 1001-5000	50
    # @limit_num_api_req_update(50)
    async def get_order_book_snapshot(self, symbol: str, limit: int = None):
        """
        :param symbol: required
        :type symbol: str
        :param limit:  Default 100; max 1000 , althought binance says 5000 max -maybe changed
        :type limit: int
        example return:
          "lastUpdateId": 15720022854,
          "bids": [
                    [
                      "3009.16000000",
                      "0.22440000"
                    ],
                    .
                    .
                    .
            ]
          "asks": [
                    [
              "3012.83000000",
              "0.13250000"
                ],
                .
                .
                .
            ]
        }
        """
        book = await self.client.get_order_book(symbol=symbol, limit=limit)
        return book

    @limit_num_api(2)
    async def get_all_order_books_best_tickers(self):
        """Best price/qty on the order book for all symbols.

        return example:
        [
            {
                "symbol": "LTCBTC",
                "bidPrice": "4.00000000",
                "bidQty": "431.00000000",
                "askPrice": "4.00000200",
                "askQty": "9.00000000"
            },
            {
                "symbol": "ETHBTC",
                "bidPrice": "0.07946700",
                "bidQty": "9.00000000",
                "askPrice": "100000.00000000",
                "askQty": "1000.00000000"
            }
        ]
        """
        weight = 3
        info = await self.client.get_orderbook_tickers()

        return info, weight


class Binance(Feed, BinanceRest):
    # UNUSED FOR NOW
    #  future binance or maybe not
    # 'STOP_LOSS_LIMIT',
    # 'TAKE_PROFIT_LIMIT'
    # supported_spot_order_types = {'LIMIT', 'MARKET', 'STOP_LOSS', 'TAKE_PROFIT', 'LIMIT_MAKER'}
    # supported_time_in_force = {'GTC', 'IOC', 'FOK'}
    # supported_candle_intervals = {'1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w',
    #                               '1M'}
    # ORDER_TYPE_LIMIT_MAKER = 'LIMIT_MAKER'  # You will only be charged a maker fee, will not match existing order, only new ones
    # ORDER_TYPE_TAKE_PROFIT = 'TAKE_PROFIT'  # won't show on order book
    # ORDER_TYPE_MARKET = 'MARKET'  # whatever the market is now
    # ORDER_TYPE_STOP_LOSS = "STOP_LOSS"  # at the price become market type
    # ORDER_TYPE_LIMIT = "LIMIT"  # need TimeInForce type
    # TIME_IN_FORCE_GTC = 'GTC'  # Good till cancelled
    # TIME_IN_FORCE_IOC = 'IOC'  # Immediate or cancel (execute all or part immediately and then cancels any unfilled portion of the order)
    # TIME_IN_FORCE_FOK = 'FOK'  # Fill or kill (fully execute all the order or none)
    # KLINE_INTERVAL_1MINUTE = '1m'
    # KLINE_INTERVAL_3MINUTE = '3m'
    # KLINE_INTERVAL_5MINUTE = '5m'
    # KLINE_INTERVAL_15MINUTE = '15m'
    # KLINE_INTERVAL_30MINUTE = '30m'
    # KLINE_INTERVAL_1HOUR = '1h'
    # KLINE_INTERVAL_2HOUR = '2h'
    # KLINE_INTERVAL_4HOUR = '4h'
    # KLINE_INTERVAL_6HOUR = '6h'
    # KLINE_INTERVAL_8HOUR = '8h'
    # KLINE_INTERVAL_12HOUR = '12h'
    # KLINE_INTERVAL_1DAY = '1d'
    # KLINE_INTERVAL_3DAY = '3d'
    # KLINE_INTERVAL_1WEEK = '1w'
    # KLINE_INTERVAL_1MONTH = '1M'
    # order_status = {'NEW', 'PARTIALLY_FILLED', 'FILLED', 'CANCELED', 'PENDING_CANCEL', 'REJECTED', 'EXPIRED'}
    # order_resp_type = {'ACK', 'RESULT', 'FULL'}
    # aggregate_info_type = {'ACK', 'RESULT', 'FULL', 'a', 'p', 'q', 'f', 'l', 'T', 'm', 'M'}
    # For accessing the data returned by Client.aggregate_trades().
    # ORDER_RESP_TYPE_ACK
    # ORDER_RESP_TYPE_RESULT
    # ORDER_RESP_TYPE_FULL
    # AGG_ID
    # AGG_PRICE
    # AGG_QUANTITY
    # AGG_FIRST_TRADE_ID
    # AGG_LAST_TRADE_ID
    # AGG_TIME
    # AGG_BUYER_MAKES
    # AGG_BEST_MATCH
    # ORDER_RESP_TYPE_ACK = 'ACK' ORDER_RESP_TYPE_RESULT = 'RESULT' ORDER_RESP_TYPE_FULL = 'FULL' AGG_ID = 'a'
    # AGG_PRICE = 'p' AGG_QUANTITY = 'q' AGG_FIRST_TRADE_ID = 'f' AGG_LAST_TRADE_ID = 'l' AGG_TIME = 'T'
    # AGG_BUYER_MAKES = 'm' AGG_BEST_MATCH = 'M' future_order_types = {'LIMIT', 'MARKET', 'STOP', 'STOP_MARKET',
    # 'TAKE_PROFIT', 'TAKE_PROFIT_MARKET', 'LIMIT_MAKER'} might need some of those variables exceptions=None,
    # log_message_on_error=False delay_start=delay_start log_message_on_error=log_message_on_error
    # exceptions=exceptions callbacks=callbacks timeout_interval=timeout_interval, timeout=timeout, , channels=channels

    CANDLE = "kline"
    TRADE = "trade"
    AGG_TRADE = "aggTrade"
    TICKER_24 = "24hrTicker"
    MINI_TICKER_24 = "24hrMiniTicker"
    BOOK_TICKER = "bookTicker"
    DEPTH_EVENT = "depthUpdate"
    BOOK = "book"
    DEPTH_100 = "depth100"
    DEPTH_1000 = "depth"

    i = 1
    MAX_NUM_STREAMS_FOR_CONNECTION = 950

    def __init__(self, client: AsyncClient, binance_socket_manager: BinanceSocketManager) -> None:
        super(Binance, self).__init__(client)
        self.init_information()
        self.binance_socket_manager = binance_socket_manager  # handle socket streams
        self.all_streams_info: dict = {}
        self._runnable_streams = []
        self._feeds_coroutine = None
        self.delay_start = 0
        self.timeout = 999999

    def add_feed(self, symbols, streams: list, candle_intervals: list = None, max_depth=0) -> None:
        if not candle_intervals:
            candle_intervals = ["1m"]
        lst = self._normalize_instance_streams_for_socket(streams, symbols, candle_intervals)
        if len(self._runnable_streams) + len(lst) > self.MAX_NUM_STREAMS_FOR_CONNECTION:
            print("too much streams on this instance")
            raise Exception("too much streams on this instance")

        self._runnable_streams = self._runnable_streams + lst
        self._runnable_streams = list(set(self._runnable_streams))
        self._add_instance_streams_info(streams, symbols, candle_intervals)

    def _normalize_instance_streams_for_socket(self, streams, symbols, candle_intervals) -> list:
        normal_stream = []
        for key in streams:
            if key == self.CANDLE:
                for candle_interval in candle_intervals:
                    normal_stream.append("@kline" + "_" + candle_interval)
            if key == self.BOOK:
                normal_stream.append("@bookTicker")
            if key == self.TRADE:
                normal_stream.append("@trade")
            if key == self.AGG_TRADE:
                normal_stream.append("@aggTrade")
            if key == self.USER:
                continue
            # if key == self.DEPTH_100:
            #     normal_stream.append("@depth@100ms")
            # if key == self.DEPTH_1000:
            #     normal_stream.append("@depth")

        ready_streams = [symbol.lower() + stream for symbol in symbols for stream in normal_stream]
        ready_streams = list(set(ready_streams))
        return ready_streams

    def _add_instance_streams_info(self, streams, symbols, candle_intervals) -> None:
        for stream in streams:
            if stream == self.CANDLE:
                if stream not in self.all_streams_info:
                    self.all_streams_info[stream] = {}
                    for candle in candle_intervals:
                        if candle not in self.all_streams_info[stream]:
                            self.all_streams_info[stream][candle] = []
                    continue
            if stream not in self.all_streams_info:
                self.all_streams_info[stream] = []
        for stream in streams:
            if stream == self.USER:
                self.all_streams_info[stream].append(True)
                continue
            if stream == self.CANDLE:
                for candle in candle_intervals:
                    for symbol in symbols:
                        self.all_streams_info[stream][candle].append(symbol)
                continue
            for symbol in symbols:
                self.all_streams_info[stream].append(symbol)

    def set_timeout(self, timeout):
        self.timeout = timeout

    def set_delay_start(self, delay_start):
        self.delay_start = delay_start

    def get_name(self) -> str:
        return self.BINANCE

    def get_streams(self) -> dict:
        return self.all_streams_info

    def get_delay_start(self):
        pass

    def get_timeout(self):
        return self.timeout

    def get_feed_socket_object(self):
        sm = self.binance_socket_manager.multiplex_socket(self._runnable_streams)
        return sm

    def get_user_socket_object(self):
        sm = self.binance_socket_manager.user_socket()
        return sm

    def get_all_exchange_feed(self) -> list[ExchangeFeed]:
        lst = []
        for event_type, value in self.all_streams_info.items():
            if event_type == self.USER:
                continue
            if event_type == self.CANDLE:
                for interval, symbols in value.items():
                    for symbol in symbols:
                        lst.append(ExchangeFeed(self.BINANCE, "", symbol, event_type, interval, {}))
                continue
            for symbol in value:
                lst.append(ExchangeFeed(self.BINANCE, "", symbol, event_type, "", {}))
        return lst

    async def normalize_msg(self, msg):
        if not msg['data']:
            return msg
        m = msg['data']
        res_type = m['e']
        d = datetime.datetime.fromtimestamp(m['E'] / 1000).strftime("%m/%d/%Y, %H:%M:%S")
        m['E'] = d

        efk = ExchangeFeed(symbol=m['s'], interval="", exchange=self.BINANCE,
                           event_type=res_type, data=m, event_time=d)
        if res_type == self.CANDLE:
            m.pop("s")
            kline = m.pop("k")
            kline['t'] = datetime.datetime.fromtimestamp(kline['t'] / 1000)
            kline['T'] = datetime.datetime.fromtimestamp(kline['T'] / 1000)
            m.update(kline)
            efk = ExchangeFeed(symbol=m['s'], interval=m['i'], exchange=self.BINANCE,
                               event_type=res_type, data=m, event_time=d)
        return efk

    def __str__(self) -> str:
        lst = self.get_all_exchange_feed()
        symbols = []
        for feed in lst:
            symbols.append(feed.symbol)
        symbols = list(set(symbols))
        c_str = f'exchange: {self.BINANCE} \n'
        c_str += f'{len(symbols)} symbols: {symbols} \n'
        c_str += f'feeds: \n'
        index = 0
        for feed in lst:
            index += 1
            c_str += f'{index}: {feed.exchange}-{feed.symbol}-{feed.event_type}-{feed.interval}'
        return c_str
