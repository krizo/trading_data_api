from typing import Dict, List
from data_structures.bst import BST
from config.consts import MAX_TRADE_POINTS_COUNT, MAX_SYMBOLS_COUNT, MAX_SYMBOLS_LENGTH
from typing import Dict, List

from config.consts import MAX_TRADE_POINTS_COUNT, MAX_SYMBOLS_COUNT, MAX_SYMBOLS_LENGTH
from data_structures.bst import BST


class Database:
    _instance = None

    def __new__(cls):
        """
        Ensures that only one instance of the Database class is created (Singleton pattern).

        @returns: The singleton instance of the Database class.
        """
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """
        Initialize the in-memory storage for trading symbols.
        This method is called only once during the lifetime of the singleton instance.
        """
        self.data_store: Dict[str, BST] = {}

    def add_batch(self, symbol: str, values: List[float]) -> str:
        """
        Add a batch of trading data for a specific symbol with validation.

        @param symbol: The financial instrument identifier.
        @param values: A list of trading price values.
        @returns: Confirmation message for the addition of batch data.
        @raises ValueError: If any validation fails (e.g., symbol length, invalid values).
        """
        # Validate the length of the symbol
        if len(symbol) > MAX_SYMBOLS_LENGTH:
            raise ValueError(f"Symbol length must not exceed {MAX_SYMBOLS_LENGTH} characters.")

        # Validate the total number of symbols
        if len(self.data_store) >= MAX_SYMBOLS_COUNT and symbol not in self.data_store:
            raise ValueError(f"Symbols limit reached ({MAX_SYMBOLS_COUNT}).")

        # Validate the size of the values list
        if len(values) == 0:
            raise ValueError("The list of trading values must contain at least 1 item.")
        if len(values) > MAX_TRADE_POINTS_COUNT:
            raise ValueError(f"The list should have at most {MAX_TRADE_POINTS_COUNT} items, not {len(values)}.")

        # Validate the values themselves
        for value in values:
            if not isinstance(value, (int, float)):
                raise ValueError("All values must be valid numbers.")
            if value < 0:
                raise ValueError("All values must be greater than 0.")

        # If symbol is not in the data store, initialize its BST
        if symbol not in self.data_store:
            self.data_store[symbol] = BST()

        bst = self.data_store[symbol]
        for value in values:
            bst.insert(value)

        return "Batch added successfully"

    def get_stats(self, symbol: str, k: int) -> Dict[str, float]:
        """
        Get statistical analysis of trading data for a specific symbol.

        @param symbol: The financial instrument identifier.
        @param k: The number of last 1e{k} data points to analyze.
        @returns: A dictionary containing the min, max, last, avg, var, and size values.
        @raises ValueError: If the symbol is not found in the database.
        """
        if symbol not in self.data_store:
            raise ValueError("Symbol not found")

        bst = self.data_store[symbol]

        return {
            "min": bst.get_stats().get('min'),
            "max": bst.get_stats().get('max'),
            "last": bst.get_stats().get('last'),
            "avg": bst.mean_value,
            "var": bst.get_stats().get('var'),
            "size": bst.get_stats().get('size')
        }

    def get_values(self, symbol: str) -> List[float]:
        """
        Get all trading values for a specific symbol, sorted in ascending order.

        @param symbol: The financial instrument identifier.
        @returns: A sorted list of all trading prices for the given symbol.
        @raises ValueError: If the symbol is not found in the database.
        """
        if symbol not in self.data_store:
            raise ValueError("Symbol not found")

        bst = self.data_store[symbol]
        return list(bst.get_all_values())

    def get_symbols(self) -> List[str]:
        """
        Get all trading symbols stored in the system.

        @returns: A list of all symbols.
        """
        from main import LOG
        LOG.info(self.data_store.keys())
        return list(self.data_store.keys())

    def clear(self):
        """
        Clear the entire data store, removing all symbols and their corresponding data.
        """
        self.data_store.clear()

    def delete_symbol(self, symbol: str) -> str:
        """
        Delete the data for a specific symbol.

        @param symbol: The financial instrument identifier.
        @returns: Confirmation message for the deletion of the symbol.
        @raises ValueError: If the symbol is not found in the database.
        """
        if symbol in self.data_store:
            del self.data_store[symbol]
            return f"Symbol {symbol} deleted successfully"
        else:
            raise ValueError(f"Symbol {symbol} not found")
