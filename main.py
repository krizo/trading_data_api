import logging
import sys

from fastapi import FastAPI
from config.db import Database
from config.logging_config import setup_logger
from models.models import AddBatchRequest

app = FastAPI(debug=True)
db = Database()

LOG = setup_logger(__name__)


@app.post("/add_batch")
async def add_batch(data: AddBatchRequest):
    """
    Add a batch of trading prices for a given financial instrument.

    - **symbol**: String identifier for the financial instrument.
    - **values**: List of up to 10,000 floating-point numbers representing trading prices ordered from oldest to newest.
    """
    symbol = data.symbol
    values = data.values
    db.add_values(symbol, values)
    return {f"Successfully added {len(values)} values for symbol '{symbol}'"}


@app.get("/get_values/{symbol}")
async def get_values(symbol: str):
    """
    Get trading values for a given financial instrument.

    - **symbol**: String identifier for the financial instrument.
    """
    values = db.get_values(symbol)
    return {"symbol": symbol, "values": values, "total_values": len(values)}


@app.delete("/delete_symbol/{symbol}")
async def delete_symbol(symbol: str):
    """
    Delete trading values for a given financial instrument.

    - **symbol**: String identifier for the financial instrument.
    """
    db.delete_symbol(symbol)
    return {"message": f"Symbol {symbol} deleted"}


@app.delete("/clear_db")
async def clear_db():
    """
    Clear the entire database.
    """
    db.clear()
    return {"message": "Database cleared"}
