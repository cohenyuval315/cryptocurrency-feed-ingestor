import asyncio
import json
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from client.util.data_classes import ExchangeFeed


def get_exchange_kafka_topics(exchange, symbols: list, streams: list, candle_intervals=None):
    if candle_intervals is None:
        candle_intervals = ["1m"]
    lst = []
    for symbol in symbols:
        for stream in streams:
            topic_stream = f"{exchange.get_name()}-{symbol}-{stream}"
            if "user" in stream:
                topic_stream = f"{exchange.get_name()}-user"
            if "kline" in stream:
                for interval in candle_intervals:
                    topic_stream = f"{exchange.get_name()}-{symbol}-{stream}-{interval}"
                    lst.append(topic_stream)
                continue
            lst.append(topic_stream)
    return lst


class BaseKafka:

    def __init__(self, bootstrap="127.0.0.1", port=9092, client_id="BotFeed", **kwargs):
        self.bootstrap = bootstrap
        self.port = port
        self.client_id = client_id


# not used in this project part
class KafkaFeedConsumer(BaseKafka):

    def __init__(self, **kwargs):

        super().__init__()
        self.consumer = None

    async def __connect(self):
        if not self.consumer:
            loop = asyncio.get_event_loop()
            self.consumer = AIOKafkaConsumer(
                bootstrap_servers=f'{self.bootstrap}:{self.port}',
                client_id=self.client_id,
                loop=loop,
            )
        await self.consumer.start()

    async def get_topics(self):
        await self.__connect()
        topics = await self.consumer.topics()
        await self.consumer.stop()
        return topics

    async def subscribe_all(self):
        await self.__connect()
        topics = await self.consumer.topics()
        self.consumer.subscribe(topics=topics)

    async def subscribe_topics(self, topics: list):
        await self.__connect()
        self.consumer.subscribe(topics=topics)

    async def _process_msg(self, msg):
        return json.loads(msg.value.decode("utf-8"))

    async def read_feed(self):
        try:
            async for msg in self.consumer:
                m = await self._process_msg(msg)
                return m
        except Exception as e:
            print(e)
            await self.stop()

    async def stop(self):
        await self.consumer.stop()


class KafkaFeedProducer(BaseKafka):
    default_key = None

    def __init__(self, topic_key=None, **kwargs):
        super().__init__()
        self.producer = None
        # self.topic_key = topic_key if topic_key else self.default_key
        self.__connect()
        self.producer_started = False

    def __connect(self):
        if not self.producer:
            loop = asyncio.get_event_loop()
            self.producer = AIOKafkaProducer(
                acks=0,
                bootstrap_servers=f'{self.bootstrap}:{self.port}',
                client_id=self.client_id,
                loop=loop,
            )

    async def write(self, topic, data):
        try:
            await self.producer.send_and_wait(topic, data)
        except Exception as e:
            print(e)
            await self.stop()

    async def write_feed(self, efk: ExchangeFeed = None, alternative_data: dict = None):
        if not self.producer_started:
            await self.producer.start()
            self.producer_started = True
        topic = f"{efk.exchange}-{efk.symbol}-{efk.event_type}"
        if efk.event_type == "user":
            topic = f"{efk.exchange}-user"
            await self.producer.send_and_wait(topic, json.dumps(alternative_data, default=str).encode('utf-8'))
            return
        if efk.event_type == "kline":
            topic = f"{efk.exchange}-{efk.symbol}-{efk.event_type}-{efk.interval}"
        try:
            data = efk.data
            if not data:
                data = alternative_data
            await self.producer.send_and_wait(topic, json.dumps(data, default=str).encode(
                'utf-8'))  # ,partition=0) todo maybe add another function for this seperate , get topic partition etc probably harder on performance
            print("kafka-fin")
        except Exception as e:
            print(e)
            await self.stop()

    async def stop(self):
        await self.producer.stop()


# <--->
# last resort for performance
#
# class CandleKafka(KafkaFeedProducer):
#     default_key = "kline"
#
#
# class UserKafka(KafkaFeedProducer):
#     default_key = "user"
#
#
# class TradeKafka(KafkaFeedProducer):
#     default_key = 'trade'
#
#
# class AggTradeKafka(KafkaFeedProducer):
#     default_key = 'aggTrade'
#
#
# class BookKafka(KafkaFeedConsumer):
#     default_key = "book"
#
#
# class DepthKafka(KafkaFeedProducer):
#     default_key = 'depth'
