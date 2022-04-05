import asyncio
import json
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer

from client.exchange.exchange_model.exchange import Exchange
from client.util.data_classes import ExchangeFeedKafka

def get_exchange_kafka_topics(exchange, symbols: list, streams: list, candle_intervals=None):
    if candle_intervals is None:
        candle_intervals = ["1m"]
    lst = []
    for symbol in symbols:
        for stream in streams:
            if "user" in streams:
                continue
            if "kline" in streams:
                for interval in candle_intervals:
                    topic_stream = f"{exchange.get_name()}-{stream}-{interval}-{symbol}"
                    lst.append(topic_stream)
            else:
                topic_stream = f"{exchange.get_name()}-{stream}-{symbol}"
                lst.append(topic_stream)
    return lst


class BaseKafka:

    def __init__(self, bootstrap="127.0.0.1", port=9092, client_id="BotFeed", **kwargs):
        self.bootstrap = bootstrap
        self.port = port
        self.client_id = client_id


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
                loop=loop
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

    async def read(self, process_msg=None):
        while True:
            try:
                # Consume messages
                async for msg in self.consumer:
                    if not msg:
                        continue
                    if process_msg:
                        m = json.loads(msg.value.decode("utf-8"))
                        # m["timestamp"] = msg.timestamp
                        # m["topic"] = msg.topic
                        await process_msg(m)
                    # print("consumed: ", msg.topic, msg.partition, msg.offset,
                    #       msg.key, msg.value, msg.timestamp)
            except Exception as e:
                print(e)

    async def stop(self):
        await self.consumer.stop()


class KafkaFeedProducer(BaseKafka):
    default_key = None
    i = -953

    def __init__(self, topic_key=None, **kwargs):
        super().__init__()
        self.producer = None
        self.topic_key = topic_key if topic_key else self.default_key
        self.__connect()
        self.producer_started = False

    def __connect(self):
        if not self.producer:
            loop = asyncio.get_event_loop()
            self.producer = AIOKafkaProducer(
                acks=0,  # fire and forget
                bootstrap_servers=f'{self.bootstrap}:{self.port}',
                client_id=self.client_id,
                loop=loop,
                linger_ms=10
            )

    async def write(self, efk: ExchangeFeedKafka, data: dict):
        if not self.producer_started:
            await self.producer.start()
            self.producer_started = True
        if self.topic_key == "user":
            topic = f"{efk.exchange}-{self.topic_key}"
        elif self.topic_key == "kline":
            topic = f"{efk.exchange}-{self.topic_key}-{efk.interval}-{efk.symbol}"
        else:
            topic = f"{efk.exchange}-{self.topic_key}-{efk.symbol}"
        # self.topics[data["exchange"]] = topic
        await self.producer.send_and_wait(topic, json.dumps(data).encode('utf-8'))
        print(self.i, " --finished writing kafka")
        self.i += 1


class CandleKafka(KafkaFeedProducer):
    default_key = "kline"


class UserKafka(KafkaFeedProducer):
    default_key = "user"


class TradeKafka(KafkaFeedProducer):
    default_key = 'trade'


class AggTradeKafka(KafkaFeedProducer):
    default_key = 'aggTrade'


class BookKafka(KafkaFeedConsumer):
    default_key = "book"


class DepthKafka(KafkaFeedProducer):
    default_key = 'depth'

    # def __init__(self, *args, snapshots_only=False, snapshot_interval=1000, **kwargs):
    #     self.snapshots_only = snapshots_only
    #     self.snapshot_interval = snapshot_interval
    #     self.snapshot_count = defaultdict(int)
    #     super().__init__(*args, **kwargs)


