import math
from typing import Dict, List

from data_structures.bst import BST


class Database:
    _instance = None

    def __new__(cls):
        """
        Ensures that only one instance of the Database class is created (Singleton pattern).
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

    def add_batch(self, symbol: str, values: List[float]):
        """
        Add a batch of trading data for a specific symbol.

        Args:
            symbol (str): The financial instrument identifier.
            values (List[float]): A list of trading price values.

        Returns:
            str: Confirmation message for the addition of batch data.
        """
        if symbol not in self.data_store:
            self.data_store[symbol] = BST()

        bst = self.data_store[symbol]
        for value in values:
            bst.insert(value)

        return "Batch added successfully"

    def get_stats(self, symbol: str, k: int) -> Dict[str, float]:
        """
        Get statistical analysis of trading data for a specific symbol.

        Args:
            symbol (str): The financial instrument identifier.
            k (int): The number of last 1e{k} data points to analyze.

        Returns:
            Dict[str, float]: A dictionary containing the min, max, last, avg, and var values.
        """
        if symbol not in self.data_store:
            raise ValueError("Symbol not found")

        bst = self.data_store[symbol]
        num_points = int(math.pow(10, k))

        min_value = bst.get_min()
        max_value = bst.get_max()
        last_value = bst.get_last()
        avg_value, var_value = bst.calculate_avg_and_var(num_points)

        return {
            "min": min_value,
            "max": max_value,
            "last": last_value,
            "avg": avg_value,
            "var": var_value,
            "size": bst.get_size()
        }

    def get_values(self, symbol: str) -> List[float]:
        """
        Get all trading values for a specific symbol, sorted in ascending order.

        Args:
            symbol (str): The financial instrument identifier.

        Returns:
            List[float]: A sorted list of all trading prices for the given symbol.
        """
        if symbol not in self.data_store:
            raise ValueError("Symbol not found")

        bst = self.data_store[symbol]
        return list(bst.inorder())

    def get_symbols(self) -> List[str]:
        """
        Get all trading symbols stored in the system.

        Returns:
            List[str]: A list of all symbols.
        """
        from main import LOG
        LOG.info(self.data_store.keys())
        return list(self.data_store.keys())

    def clear(self):
        """
        Clear the entire data store, removing all symbols and their corresponding data.
        """
        self.data_store.clear()

    def delete_symbol(self, symbol: str):
        """
        Delete the data for a specific symbol.

        Args:
            symbol (str): The financial instrument identifier.

        Returns:
            str: Confirmation message for the deletion of the symbol.
        """
        if symbol in self.data_store:
            del self.data_store[symbol]
            return f"Symbol {symbol} deleted successfully"
        else:
            raise ValueError(f"Symbol {symbol} not found")
