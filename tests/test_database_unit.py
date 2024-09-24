import random

import numpy as np
import pytest

from config.db import Database
from helpers.assertions import assert_equals


@pytest.fixture(autouse=True)
def db():
    """
    Fixture to create a new instance of the Database class before each test.
    """
    db = Database()
    db.clear()
    return db


@pytest.mark.unit
def test_add_batch(db):
    """
    Test adding a batch of trading data to the database.
    """
    symbol = "AAPL"
    values = [150.1, 152.3, 151.0]

    # Add the batch of data
    result = db.add_batch(symbol, values)
    assert result == "Batch added successfully"

    # Verify the data was added correctly
    stored_values = db.get_values(symbol)
    assert stored_values == values  # BST stores values in sorted order


@pytest.mark.unit
def test_get_stats(db):
    """
    Test retrieving statistics from the database.
    """
    symbol = "AAPL"
    values = [round(random.uniform(0.01, 1000.0), 2) for _ in range(10)]

    # Add the batch of data
    db.add_batch(symbol, values)
    assert db.get_symbols() == [symbol]

    stats = db.get_stats(symbol, k=1)

    assert_equals(stats["min"], min(values), 'min')
    assert_equals(stats["max"], max(values), 'max')
    assert_equals(stats["last"], values[-1], 'last')
    assert_equals(pytest.approx(stats["avg"], 0.01), np.mean(values), 'avg')
    assert_equals(pytest.approx(stats["var"], 0.01), np.var(values), 'var')


@pytest.mark.unit
def test_get_values(db):
    """
    Test retrieving all values for a specific symbol.
    """
    symbol = "AAPL"
    values = [150.1, 152.3, 151.0]

    # Add the batch of data
    db.add_batch(symbol, values)

    # Get all values for the symbol
    stored_values = db.get_values(symbol)
    assert stored_values == values


@pytest.mark.unit
def test_clear(db):
    """
    Test clearing the entire database.
    """
    symbol1 = "AAPL"
    symbol2 = "GOOG"
    values1 = [150.1, 152.3, 151.0]
    values2 = [2800.5, 2820.4, 2795.3]

    # Add batches of data
    db.add_batch(symbol1, values1)
    db.add_batch(symbol2, values2)

    # Clear the database
    db.clear()

    # Verify that the database is empty
    with pytest.raises(ValueError):
        db.get_values(symbol1)
    with pytest.raises(ValueError):
        db.get_values(symbol2)


@pytest.mark.unit
def test_delete_symbol(db):
    """
    Test deleting a specific symbol from the database.
    """
    symbol = "AAPL"
    values = [150.1, 152.3, 151.0]

    # Add the batch of data
    db.add_batch(symbol, values)

    # Delete the symbol
    result = db.delete_symbol(symbol)
    assert result == f"Symbol {symbol} deleted successfully"

    # Verify the symbol was deleted
    with pytest.raises(ValueError):
        db.get_values(symbol)


@pytest.mark.unit
def test_delete_non_existent_symbol(db):
    """
    Test deleting a symbol that does not exist.
    """
    with pytest.raises(ValueError, match="Symbol XYZ not found"):
        db.delete_symbol("XYZ")
