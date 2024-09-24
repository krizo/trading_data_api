from fastapi import FastAPI, HTTPException
from typing import List

from config.db import Database
from config.logging_config import setup_logger
from models.add_batch_model import AddBatchRequest
from models.stats_response_model import StatsResponse

db = Database()
app = FastAPI()
LOG = setup_logger(__name__)


# Endpoint to add batch of trading data
@app.post("/add_batch/")
async def add_batch(request: AddBatchRequest):
    """
    Add a batch of trading data for a specific symbol.

    Args:
        request (AddBatchRequest): A request body containing the symbol and a list of trading values.

    Returns:
        dict: A message confirming the batch data addition.
    """
    try:
        message = db.add_batch(request.symbol, request.values)
        return {"message": message}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Endpoint to get statistics for a symbol
@app.get("/stats/", response_model=StatsResponse)
async def get_stats(symbol: str, k: int):
    """
    Get statistical analysis for a specific symbol based on the last 1e{k} data points.

    Args:
        symbol (str): The financial instrument identifier.
        k (int): An integer from 1 to 8, representing the number of last data points to analyze.

    Returns:
        StatsResponse: A response containing min, max, last, avg, and var values.
    """
    try:
        stats = db.get_stats(symbol, k)
        return StatsResponse(**stats)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# Endpoint to get all values for a symbol
@app.get("/get_values/{symbol}", response_model=List[float])
async def get_values(symbol: str):
    """
    Retrieve all trading values for a specific symbol, sorted in ascending order.

    Args:
        symbol (str): The financial instrument identifier.

    Returns:
        List[float]: A list of sorted trading prices for the given symbol.
    """
    try:
        values = db.get_values(symbol)
        return values
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/symbols/", response_model=List[str])
async def get_symbols():
    """
    Retrieve all trading values for a specific symbol, sorted in ascending order.

    Args:
        symbol (str): The financial instrument identifier.

    Returns:
        List[float]: A list of sorted trading prices for the given symbol.
    """
    try:
        values = db.get_symbols()
        return values
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# Endpoint to clear all data
@app.delete("/clear/")
async def clear_database():
    """
    Clear the entire data store, removing all symbols and their corresponding data.

    Returns:
        dict: A message confirming that the database was cleared.
    """
    db.clear()
    return {"message": "Database cleared successfully"}


# Endpoint to delete a specific symbol
@app.delete("/delete_symbol/")
async def delete_symbol(symbol: str):
    """
    Delete data for a specific symbol.

    Args:
        symbol (str): The financial instrument identifier.

    Returns:
        dict: A message confirming the deletion of the symbol.
    """
    try:
        message = db.delete_symbol(symbol)
        return {"message": message}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
