# Trading Data API

## Overview

The Trading Data API is designed for managing and analyzing trading data. The system supports various operations including adding trading data, retrieving statistics, and managing symbols. The API is built using Python and FastAPI, with a focus on performance and scalability. Key technologies include:

- **FastAPI**: Framework for building APIs with Python.
- **Pydantic**: Data validation and settings management.
- **Requests**: HTTP library for making API requests.
- **pytest**: Testing framework for ensuring code quality and correctness.
- **Swagger/OpenAPI**: Documentation and interactive API exploration.

## Setup

1. **Install Dependencies**: Ensure that all dependencies are installed.

    ```bash
    pip install -r requirements.txt
    ```

2. **Run the FastAPI Server**: Start the FastAPI server using Uvicorn.

    ```bash
    uvicorn main:app --reload
    ```

    This will start the server at [http://localhost:8000](http://localhost:8000). You can access the interactive API documentation provided by Swagger at:

    [http://localhost:8000/docs](http://localhost:8000/docs)

## Endpoints

For detailed information about the API endpoints and their usage, please refer to the Swagger documentation:

- [API Documentation](http://localhost:8000/docs)
- [Redoc Documentation](http://localhost:8000/redoc)

## Usage

### Adding Data

To add a batch of trading data for a financial instrument, send a POST request to `/add_batch`.

### Retrieving Statistics

To retrieve statistical analysis of trading data, send a GET request to `/stats`.

### Managing Symbols

- **Retrieve Symbols**: GET `/get_symbols`
- **Delete Symbol**: DELETE `/delete_symbol/{symbol}`


## Project Overview

This project is a FastAPI-based application for managing and analyzing trading data. The application allows users to add, retrieve, delete trading data, and perform statistical analysis on this data. Below is a brief description of the different modules within the project and their responsibilities:

### Modules

#### `main.py`

- **Purpose**: This is the main entry point for the FastAPI application.
- **Responsibilities**:
  - Defines API endpoints for adding, retrieving, deleting trading data, and performing statistical analysis.
  - Uses the `Database` class for managing data and interacting with the database.
  - Configures logging and sets up the FastAPI application.

#### `config/db.py`

- **Purpose**: Manages the in-memory database for storing and retrieving trading data.
- **Responsibilities**:
  - Provides methods to add, retrieve, delete trading data.
  - Performs statistical analysis on trading data.
  - Ensures that the database adheres to predefined limits for symbols and trade points.

#### `config/logging_config.py`

- **Purpose**: Configures the logging system for the application.
- **Responsibilities**:
  - Sets up a logger with a specified format and logging level.
  - Ensures that logs are output to the console for easy monitoring.

#### `models/add_batch_model.py`

- **Purpose**: Defines the data model for adding a batch of trading prices.
- **Responsibilities**:
  - Uses Pydantic to validate and serialize the input data.
  - Ensures that the symbol is within the allowed length and all values are greater than zero.

#### `models/stats_response_model.py`

- **Purpose**: Defines the data model for the response of the statistical analysis endpoint.
- **Responsibilities**:
  - Uses Pydantic to validate and serialize the response data.
  - Provides a structured format for returning statistical metrics (min, max, last, avg, variance).

#### `helpers/decorators.py`

- **Purpose**: Provides utility decorators for various functionalities.
- **Responsibilities**:
  - `log_execution_time`: Logs the execution time of functions to monitor performance.

#### `helpers/generators.py`

- **Purpose**: Provides utility functions for generating and processing data.
- **Responsibilities**:
  - `SymbolGenerator`: Generates unique trading symbols.
  - `chunk_data`: Splits data into chunks of a specified size.
  - `generate_values`: Generates random trading values for testing purposes.

#### `helpers/assertions.py`

- **Purpose**: Provides utility functions for asserting values in tests.
- **Responsibilities**:
  - `assert_equals`: Compares actual and expected values, allowing for optional rounding and custom error messages.


### Testing

Testing is conducted using `pytest`. The tests cover a range of scenarios to ensure the API behaves as expected under various conditions. The tests are categorized into positive, negative, and performance scenarios:

### Positive Tests

1. **Adding Data**: Tests whether adding a batch of trading data to the system is successful.
2. **Retrieving Values**: Verifies if the trading values can be correctly retrieved for a given symbol.
3. **Retrieving Statistics**: Ensures that statistical data (e.g., min, max, average, variance) is accurately calculated and returned for a given symbol.

**Running Positive Tests:**

```bash
pytest -s "tests/test_add_batch_positive.py"
```

You should get similar output to the following:

```commandline
tests/test_add_batch_positive.py ...2024-09-13 13:15:09,956: INFO : Checking Symbol: expected RH1K, got RH1K.
.2024-09-13 13:15:09,961: INFO : Checking Symbol: expected JO4S, got JO4S.
.2024-09-13 13:15:09,966: INFO : Checking Symbol: expected QAML, got QAML.
.2024-09-13 13:15:09,977: INFO : Execution time of GET_STATS: 4.126 milliseconds
2024-09-13 13:15:09,979: INFO : Checking /size/ 'last' value: expected 10000, got 10000.
.2024-09-13 13:15:09,985: INFO : Execution time of GET_STATS: 2.259 milliseconds
2024-09-13 13:15:09,985: INFO : Checking /size/ 'last' value: expected 2, got 2.
.2024-09-13 13:15:09,990: INFO : Execution time of GET_STATS: 2.088 milliseconds
2024-09-13 13:15:09,990: INFO : Checking /size/ 'last' value: expected 1, got 1.
```


### Negative Tests

1. **Batch Size Exceedance**: Tests the system's response when attempting to add more than the allowed number of data points (e.g., more than 10,000 values).
2. **Empty Data Array**: Verifies the system's behavior when an empty data array is submitted.
3. **Invalid Data Format**: Checks the response when invalid data formats (e.g., strings instead of numbers) are submitted.
4. **Negative Values**: Ensures that the system correctly rejects negative values in the data array.
5. **Symbol Length**: Tests the system’s response to symbols that exceed the maximum allowed length.
6. **Symbol Limit**: Validates the system's handling of the maximum number of unique symbols allowed.

To run negative tests only, use the following command:

```bash
pytest -s "tests/test_add_batch_negative.py"
```

You should get similar output to the following:

```commandline
tests/test_add_batch_negative.py 2024-09-13 13:15:00,443: INFO : Check expected error message: list should have at most 10000 items after validation, not 10001
.2024-09-13 13:15:00,447: INFO : Check expected error message: list should have at least 1 item after validation, not 0
.2024-09-13 13:15:00,450: INFO : Check expected error message: input should be a valid number, unable to parse string as a number
.2024-09-13 13:15:00,453: INFO : Check expected error message: value error, all values must be greater than 0.
.2024-09-13 13:15:00,459: INFO : Check expected error message: value error, symbol length must not exceed 4 characters.
.2024-09-13 13:15:00,477: INFO : Check expected error message: symbols limit reached (10)
```

### Performance Tests

1. **Statistics Calculation**: Measures the system's performance and accuracy when retrieving statistics with varying values of `k`. Here, k represents the number of data points as a power of 10. For example, k=1 corresponds to 10 data points, k=2 corresponds to 100 data points, and so on up to k=MAX_K_VALUE. Tests include generating large volumes of data and verifying that statistical calculations are performed correctly and efficiently.

To run stats endpoint performance tests only, use the following command:

```bash
pytest -s "tests/tests_stats_performance.py"
```

You should get similar output to the following:

```commandline
tests/tests_stats_performance.py 2024-09-13 13:15:17,586: INFO : Execution time of GET_STATS: 3.272 milliseconds
2024-09-13 13:15:17,586: INFO : Checking stats["size"]: expected 10, got 10.
.2024-09-13 13:15:17,591: INFO : Execution time of GET_STATS: 2.316 milliseconds
2024-09-13 13:15:17,591: INFO : Checking stats["size"]: expected 100, got 100.
.2024-09-13 13:15:17,597: INFO : Execution time of GET_STATS: 2.944 milliseconds
2024-09-13 13:15:17,597: INFO : Checking stats["size"]: expected 1000, got 1000.
.2024-09-13 13:15:17,617: INFO : Execution time of GET_STATS: 7.180 milliseconds
2024-09-13 13:15:17,618: INFO : Checking stats["size"]: expected 10000, got 10000.
.2024-09-13 13:15:17,732: INFO : Execution time of GET_STATS: 31.008 milliseconds
2024-09-13 13:15:17,741: INFO : Checking stats["size"]: expected 100000, got 100000.
.2024-09-13 13:15:18,838: INFO : Execution time of GET_STATS: 205.198 milliseconds
2024-09-13 13:15:18,969: INFO : Checking stats["size"]: expected 1000000, got 1000000.
.2024-09-13 13:15:29,527: INFO : Execution time of GET_STATS: 1813.164 milliseconds
2024-09-13 13:15:30,465: INFO : Checking stats["size"]: expected 10000000, got 10000000.
.2024-09-13 13:17:28,029: INFO : Execution time of GET_STATS: 23010.237 milliseconds
2024-09-13 13:17:52,813: INFO : Checking stats["size"]: expected 100000000, got 100000000.
```




