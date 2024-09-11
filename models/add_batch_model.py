from pydantic import BaseModel, conlist


class AddBatchRequest(BaseModel):
    symbol: str
    values: conlist(item_type=float, min_length=1, max_length=10000)
