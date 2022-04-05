import dataclasses


@dataclasses.dataclass(frozen=True)
class RateLimit:
    type: str
    interval: str
    interval_num: int
    limit: int


@dataclasses.dataclass(frozen=True)
class ExchangeFeedKafka:
    exchange: str
    event: str
    interval: str
    symbol: str



