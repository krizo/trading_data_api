from pydantic import BaseModel


class StatsResponse(BaseModel):
    min: float
    max: float
    last: float
    avg: float
    var: float
