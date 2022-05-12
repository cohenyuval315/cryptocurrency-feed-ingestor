import asyncio
import os
import pathlib
from binance import AsyncClient, BinanceSocketManager
import numpy as np
from client.creds.creds_helpers import load_correct_key_info, load_config
from client.exchange.binance_impl import Binance
from client.handlers.feed_handler import FeedHandler
from client.kafka.kafka_impl import CandleKafka, TradeKafka, UserKafka, BookKafka, AggTradeKafka, KafkaFeedProducer, \
    KafkaFeedConsumer
import atexit
import multiprocessing as mp
from multiprocessing import Process
import time
from client.strategy.interval_strats.dollar_cost_averaging import DCA

filename = "creds_keys.yml"
abo_path = os.path.abspath(__file__).replace(os.path.basename(__file__), "") + r"creds\\"
filepath = pathlib.Path(abo_path, filename)
binance_api_key, binance_api_secret = load_correct_key_info(load_config(filepath), "binance")

CANDLE = "kline"
USER = "user"
TRADE = "trade"
BOOK = "book"
AGG_TRADE = "aggTrade"

# DEPTH_100_ms = "depth100"
# DEPTH_1000_ms = "depth"
# DEPTH_NUM = "100depth"


# async def interval_s():
#     client = await AsyncClient.create(api_key=api_key, api_secret=api_secret)
#     bsm = BinanceSocketManager(client=client)
#     binance = Binance(client, bsm)
#     dca = DCA("DCA", "dollar cost averaging", ["BTCUSDT"], 40, binance, 1, "day", False, None, None, None, None, None,
#               False,
#               True, "txt", False, True)
#     try:
#         await dca.start()
#     except Exception as e:
#         print(e)
#         await client.close_connection()


async def feed():
    client = await AsyncClient.create(api_key=binance_api_key, api_secret=binance_api_secret)
    bsm = BinanceSocketManager(client=client)

    # max 5 binances instances (= 5 connections max, with 950 max streams each)| calculations: not counting user stream
    # -> number of  streams * number of symbols -> example: trade,aggtrade, candle | btcusdt,bnbusdt -> 6 streams
    # (candle interval default "1m")| if candle interval present-> number of symbols * number of candle intervals +
    # number of streams * number of symbols|-> example: trade,candle | 1m,5m,1d | btcusdt ,bnbusdt  -> 1 * 2 + 3 * 2
    # - > 8
    binance1 = Binance(client, bsm)
    binance2 = Binance(client, bsm)
    binance3 = Binance(client, bsm)
    # binance4 = Binance(client, bsm, kafka)
    # binance5 = Binance(client, bsm, kafka)

    symbols = await binance1.get_spot_symbols_names()
    #
    # symbols = symbols[:100]
    splits = np.array_split(symbols, 3)
    s1 = splits[0]
    s2 = splits[1]
    s3 = splits[2]
    max_streams_num_per_connection = 953  # in my environment

    binance1.add_feed(symbols=s1, streams=[USER, CANDLE])
    binance2.add_feed(symbols=s2, streams=[USER, CANDLE])
    binance3.add_feed(symbols=s3, streams=[USER, CANDLE])

    kafka = KafkaFeedProducer()
    fh = FeedHandler([binance1, binance2], callback=kafka.write_feed)

    feeds = fh.get_exchanges_feeds()
    for exchange_feed in feeds:
        await kafka.write_feed(exchange_feed)

    consumer = KafkaFeedConsumer()
    await consumer.subscribe_all()

    tasks = [fh.start_feed(), consume(consumer)]
    await asyncio.gather(*tasks, return_exceptions=True)


async def consume(consumer):
    while True:
        m = await consumer.read_feed()


def feeds_init():
    start_time = time.time()
    try:
        asyncio.run(feed())

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


# def run_interval_strategies():
#     asyncio.run(interval_s())


def run_realtime_strategies():
    asyncio.run(real_time_s())


async def real_time_s():
    pass


def p4():
    print("NotImplementedYet")


# i got 4 cpu cores
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    p1 = Process(target=feeds_init, args=())
    # p2 = Process(target=run_interval_strategies, args=())
    # p3 = Process(target=run_realtime_strategies, args=())
    # p4 = Process(target=, args=(0,))

    p1.start()
    # p2.start()
    # p3.start()
    # p4.start()

    p1.join()
    # p2.join()
    # p3.join()
    # p4.join()


@atexit.register
def kill_children():
    [p.kill() for p in mp.active_children()]
