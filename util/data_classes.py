import dataclasses


@dataclasses.dataclass(frozen=True)
class RateLimit:
    type: str
    interval: str
    interval_num: int
    limit: int


@dataclasses.dataclass(frozen=True)
class ExchangeFeed:
    # maybe split all
    exchange: str
    event_time: str
    symbol: str
    event_type: str
    interval: str = None
    data: dict = None
