from pydantic import BaseModel, conlist, validator, constr

from config.consts import MAX_TRADE_POINTS_COUNT, MAX_SYMBOLS_LENGTH


class AddBatchRequest(BaseModel):
    symbol: constr(max_length=10)
    values: conlist(item_type=float, min_length=1, max_length=MAX_TRADE_POINTS_COUNT)

    @validator('values', each_item=True)
    def check_greate_than_zero(cls, value):
        if value < 0:
            raise ValueError('All values must be greater than 0.')
        return value

    @validator('symbol')
    def check_symbol_length(cls, symbol):
        if len(symbol) > MAX_SYMBOLS_LENGTH:
            raise ValueError(f'Symbol length must not exceed {MAX_SYMBOLS_LENGTH} characters.')
        return symbol
