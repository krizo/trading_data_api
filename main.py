from fastapi import FastAPI, HTTPException
from config.db import Database
from config.logging_config import setup_logger
from models.add_batch_model import AddBatchRequest
from models.stats_response_model import StatsResponse

# Initialize the database and FastAPI app
db = Database()
app = FastAPI(debug=True)

# Set up the logger
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
    try:
        db.add_batch(symbol, values)
    except HTTPException as e:
        LOG.error(f"Failed to add batch: {e.detail}")
        raise e
    return {"message": f"Successfully added {len(values)} values for symbol '{symbol}'"}


@app.get("/get_values/{symbol}")
async def get_values(symbol: str):
    """
    Get all trading values for a given financial instrument.

    - **symbol**: String identifier for the financial instrument.
    """
    try:
        values = db.get_values(symbol)
    except HTTPException as e:
        LOG.error(f"Failed to get values: {e.detail}")
        raise e
    return {"symbol": symbol, "values": values, "total_values": len(values)}


@app.delete("/delete_symbol/{symbol}")
async def delete_symbol(symbol: str):
    """
    Delete trading values for a given financial instrument.

    - **symbol**: String identifier for the financial instrument.
    """
    try:
        db.delete_symbol(symbol)
    except HTTPException as e:
        LOG.error(f"Failed to delete symbol: {e.detail}")
        raise e
    return {"message": f"Symbol {symbol} deleted"}


@app.delete("/clear_db")
async def clear_db():
    """
    Clear the entire database.
    """
    db.clear()
    LOG.info("Database cleared")
    return {"message": "Database cleared"}


@app.get("/stats/", response_model=StatsResponse)
async def get_stats(symbol: str, k: int):
    """
    Perform statistical analysis on recent trading data for a given symbol.

    - **symbol**: Financial instrument identifier.
    - **k**: An integer from 1 to 8, specifying the number of last 1e{k} data points to analyze.
    Returns statistics including min, max, last, average, and variance.
    """
    try:
        stats = db.calculate_stats(symbol, k)
    except HTTPException as e:
        LOG.error(f"Failed to calculate stats: {e.detail}")
        raise e
    return stats
