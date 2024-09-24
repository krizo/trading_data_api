from collections import deque
from typing import List, Dict, Optional


class Node:
    def __init__(self, value: float):
        """
        Initialize a new Node in the AVL Tree.

        @param value: The trading price value to store in the node.
        """
        self.value = value
        self.left = None
        self.right = None
        self.height = 1  # Height of the node for balancing
        self.count = 1  # Number of occurrences of this value (handles duplicates)


class AVLTree:
    def __init__(self):
        """
        Initialize an empty AVL Tree with statistics tracking and
        insertion order tracking using a deque.
        """
        self.root = None
        self.last_inserted_value = None  # Tracks the last inserted value
        self.min_value = float('inf')  # Tracks the minimum value in the tree
        self.max_value = float('-inf')  # Tracks the maximum value in the tree
        self.sum_values = 0.0  # Tracks the sum of all inserted values
        self.count_values = 0  # Tracks the number of inserted values (nodes)
        self.mean_value = 0.0  # Tracks the mean value of all inserted data
        self.sum_of_squares = 0.0  # Tracks the sum of squares for variance calculation
        self.total_size = 0  # Tracks the total number of inserted elements (including duplicates)
        self.insertion_order = deque()  # Deque to track the order of inserted values

        # Cache for statistics
        self._stats_cache = None  # Cached statistics (min, max, avg, var, size)
        self._cache_last_n = None  # Last n values used in cache

    def insert(self, value: float):
        """
        Insert a value into the AVL Tree and update statistics.

        @param value: The trading price value to insert.
        """
        self.root = self._insert(self.root, value)  # Insert the new value into the tree
        self.last_inserted_value = value  # Update the last inserted value
        self.insertion_order.append(value)  # Track the insertion order

        # Update statistics
        self.min_value = min(self.min_value, value)
        self.max_value = max(self.max_value, value)
        self.count_values += 1
        self.sum_values += value
        self.total_size += 1

        # Incrementally calculate the new mean
        old_mean = self.mean_value
        self.mean_value = self.sum_values / self.count_values

        if self.count_values > 1:
            # Update the sum of squares for variance calculation. Only when needed (more than 2 elements in the tree)
            self.sum_of_squares += (value - old_mean) * (value - self.mean_value)

        # Invalidate cache
        self._stats_cache = None
        self._cache_last_n = None

    def _insert(self, node: Optional[Node], value: float) -> Node:
        """
        Helper method to recursively insert a value into the AVL Tree while maintaining balance.

        @param node: The current node being examined.
        @param value: The value to insert.
        @returns: The updated node after insertion.
        """
        if node is None:
            return Node(value)

        if value < node.value:
            node.left = self._insert(node.left, value)
        elif value > node.value:
            node.right = self._insert(node.right, value)
        else:
            node.count += 1
            return node

        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))
        balance = self._get_balance(node)

        if balance > 1:
            if value < node.left.value:
                return self._right_rotate(node)
            else:
                node.left = self._left_rotate(node.left)
                return self._right_rotate(node)

        if balance < -1:
            if value > node.right.value:
                return self._left_rotate(node)
            else:
                node.right = self._right_rotate(node.right)
                return self._left_rotate(node)

        return node

    def _left_rotate(self, z: Node) -> Node:
        """
        Perform a left rotation on the given node.

        @param z: The root of the subtree to rotate.
        @returns: The new root after rotation.
        """
        y = z.right
        T2 = y.left
        y.left = z
        z.right = T2
        z.height = 1 + max(self._get_height(z.left), self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))
        return y

    def _right_rotate(self, z: Node) -> Node:
        """
        Perform a right rotation on the given node.

        @param z: The root of the subtree to rotate.
        @returns: The new root after rotation.
        """
        y = z.left
        T3 = y.right
        y.right = z
        z.left = T3
        z.height = 1 + max(self._get_height(z.left), self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))
        return y

    def _get_height(self, node: Optional[Node]) -> int:
        """
        Get the height of the node.

        @param node: The node whose height is to be checked.
        @returns: The height of the node.
        """
        if not node:
            return 0
        return node.height

    def _get_balance(self, node: Optional[Node]) -> int:
        """
        Calculate the balance factor of the node.

        @param node: The node whose balance is to be calculated.
        @returns: The balance factor.
        """
        if not node:
            return 0
        return self._get_height(node.left) - self._get_height(node.right)

    def get_stats(self, last_n: int = None) -> Dict[str, Optional[float]]:
        """
        Get the current statistics (min, max, last, avg, var, size).
        If last_n is specified, compute statistics based on the last n inserted values.
        Uses cache to optimize repeated queries.

        @param last_n: Number of last inserted values to include in the statistics (if None, include all records).
        @returns: A dictionary containing min, max, last, avg, var, and size.
        """
        if self.count_values == 0:
            return {
                "min": None,
                "max": None,
                "last": None,
                "avg": None,
                "var": None,
                "size": None
            }

        # Check if the requested last_n matches the cached result
        if self._stats_cache is not None and self._cache_last_n == last_n:
            return self._stats_cache

        values = list(self.insertion_order)[-last_n:] if last_n else list(self.insertion_order)

        min_value = min(values)
        max_value = max(values)
        last_value = values[-1]
        avg_value = sum(values) / len(values)
        variance = sum((x - avg_value) ** 2 for x in values) / len(values) if len(values) > 1 else 0.0
        size = len(values)

        stats = {
            "min": min_value,
            "max": max_value,
            "last": last_value,
            "avg": avg_value,
            "var": variance,
            "size": size
        }

        # Update cache
        self._stats_cache = stats
        self._cache_last_n = last_n

        return stats

    def get_all_values(self) -> List[float]:
        """
        Get all values stored in the AVL Tree in sorted order.

        @returns: A list of all values in the AVL Tree, sorted in ascending order.
        """
        values = []
        self._inorder_traversal(self.root, values)
        return values

    def _inorder_traversal(self, node: Optional[Node], values: List[float]):
        """
        Perform in-order traversal to gather all values from the AVL Tree.

        @param node: The current node in the tree.
        @param values: List to collect values in sorted order.
        """
        if node is None:
            return
        self._inorder_traversal(node.left, values)
        values.extend([node.value] * node.count)
        self._inorder_traversal(node.right, values)
