from pydantic import BaseModel, conlist

from config.consts import MAX_TRADE_POINTS_COUNT


class AddBatchRequest(BaseModel):
    symbol: str
    values: conlist(item_type=float, min_length=1, max_length=MAX_TRADE_POINTS_COUNT)
