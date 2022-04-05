import asyncio
import os
import pathlib

from binance import AsyncClient, BinanceSocketManager
import numpy as np

from client.creds.login_handler import load_correct_key_info, load_config
from client.exchange.binance_impl import Binance
from client.handlers.feed_handler import FeedHandler
from client.backend.kafka_impl import CandleKafka, TradeKafka, UserKafka, BookKafka, AggTradeKafka
import atexit
import multiprocessing as mp
from multiprocessing import Queue, Process, Manager
import time
from client.strategy.interval_strats.dollar_cost_averaging import DCA

filename = "creds_keys.yml"

abo_path = os.path.abspath(__file__).replace(os.path.basename(__file__), "") + r"creds\\"
filepath = pathlib.Path(abo_path, filename)
api_key, api_secret = load_correct_key_info(load_config(filepath))


# DEPTH_100_ms = "depth100"
# DEPTH_1000_ms = "depth"
# DEPTH_NUM = "100depth"


async def interval_s():
    client = await AsyncClient.create(api_key=api_key, api_secret=api_secret)
    bsm = BinanceSocketManager(client=client)
    binance = Binance(client, bsm)
    dca = DCA("DCA", "dollar cost averaging", ["BTCUSDT"], 40, binance, 1, "day", False, None, None, None, None, None,
              False,
              True, "txt", False, True)
    try:
        await dca.start()
    except Exception as e:
        print(e)
        await client.close_connection()

async def feed(d):
    CANDLE = "kline"
    USER = "user"
    TRADE = "trade"
    BOOK = "book"
    AGG_TRADE = "aggTrade"
    candle_kafka = CandleKafka()
    trade_kafka = TradeKafka()
    user_kafka = UserKafka()
    book_kafka = BookKafka()
    agg_kafka = AggTradeKafka()
    kafka = {CANDLE: candle_kafka, TRADE: trade_kafka,
             AGG_TRADE: agg_kafka, USER: user_kafka, BOOK: book_kafka}
    client = await AsyncClient.create(api_key=api_key, api_secret=api_secret)
    bsm = BinanceSocketManager(client=client)
    binance = Binance(client, bsm, kafka)
    binance1 = Binance(client, bsm, kafka)
    binance2 = Binance(client, bsm, kafka)
    # make generci with quupe

    symbols = await binance.get_spot_symbols_names()
    splits = np.array_split(symbols, 3)
    s1 = splits[0]
    s2 = splits[1]
    s3 = splits[2]

    if d == 0:
        pass
    # symbols = symbols[:max_length]
    else:
        pass
    #        symbols = symbols[max_length:max_length * 2]
    max_length = 953

    # symbols1 = symbols[:max_length]
    # print(len(symbols1))
    binance.add_feed(symbols=s1, streams=[USER, CANDLE])
    # symbols2 = symbols[max_length:]
    # print(len(symbols2))
    binance1.add_feed(symbols=s2, streams=[USER, CANDLE])
    binance2.add_feed(symbols=s3, streams=[USER, CANDLE])

    # max 5 binance instances each can have up to ~950 streams
    fh = FeedHandler([binance, binance1, binance2])
    topics = fh.get_exchanges_kafka_streams()

    for exchange_feed in topics:
        event_type = exchange_feed.event
        await kafka[event_type].write(exchange_feed, "")

    # consumer = KafkaFeedConsumer()
    # await consumer.subscribe_all()
    tasks = [fh.start_feed()]  # , consumer.read()]
    await asyncio.gather(*tasks, return_exceptions=True)


def feeds_init(d):
    start_time = time.time()
    try:
        asyncio.run(feed(d))
    except Exception as e:
        print(e)
        print("interrupt:")
        end_time_ex = time.time()
        run_time_ex = end_time_ex - start_time
        print(run_time_ex)
    finally:
        print("crash/end")
        end_time = time.time()
        run_time = end_time - start_time
        print(run_time)


def run_interval_strategies():
    asyncio.run(interval_s())


def run_realtime_strategies():
    asyncio.run(real_time_s())


async def real_time_s():
    pass


def p4():
    print("NotImplementedYet")


if __name__ == '__main__':
    # MORE STREAMS WITH MORE FEED

    #

    #
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    p1 = Process(target=feeds_init, args=(1,))
    p2 = Process(target=run_interval_strategies, args=())
    p3 = Process(target=run_realtime_strategies, args=())
    # p4 = Process(target=feeds_init, args=(0,))  # for csv and data handling

    p1.start()
    p2.start()
    p3.start()
    # p4.start()

    p1.join()
    p2.join()
    p3.join()
    # p4.join()


@atexit.register
def kill_children():
    [p.kill() for p in mp.active_children()]

