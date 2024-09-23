from exchange import models


def buy_from_exchange(coin: models.Coin, amount: int) -> bool:  # noqa: ARG001
    return True


def minimum_settlement_threshold(coin: models.Coin) -> int:
    match coin:
        case models.Coin.USD:
            return 0
        case models.Coin.ABAN:
            return 10


def get_rate_by_usd(coin: models.Coin) -> int:
    match coin:
        case models.Coin.USD:
            return 1
        case models.Coin.ABAN:
            return 4
