from typing import List, Dict
from fastapi import HTTPException


class SymbolNotFound(HTTPException):
    def __init__(self, symbol: str):
        super().__init__(status_code=404, detail=f"Symbol {symbol} not found")


class Database:
    """
    In-memory database storing values as dicts
    """

    def __init__(self):
        self.data: Dict[str, List[float]] = {}

    def add_values(self, symbol: str, values: List[float]):
        # Can be replaced as setdefault?
        if symbol in self.data:
            self.data[symbol].extend(values)
        else:
            self.data[symbol] = values

    def get_values(self, symbol: str) -> List[float]:
        if symbol not in self.data:
            raise SymbolNotFound(symbol)
        return self.data[symbol]

    def delete_symbol(self, symbol: str):
        if symbol in self.data:
            del self.data[symbol]
        else:
            raise SymbolNotFound(symbol)

    def get_value(self, symbol: str) -> List[float]:
        value = self.data.get(symbol)
        if not value:
            raise SymbolNotFound(symbol)
        return value

    def clear(self):
        self.data.clear()
