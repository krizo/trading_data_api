from typing import List, Dict


class Node:
    def __init__(self, value: float):
        """
        Initialize a new Node in the BST.

        @param value: The trading price value to store in the node.
        """
        self.value = value  # The value of the trading price
        self.left = None  # Left subtree (values less than the current node)
        self.right = None  # Right subtree (values greater than the current node)
        self.count = 1  # Number of occurrences of this value (handles duplicates)


class BST:
    def __init__(self):
        """
        Initialize an empty Binary Search Tree with statistics tracking.
        """
        self.root = None  # The root of the tree
        self.last_inserted_value = None  # Tracks the last inserted value
        self.min_value = float('inf')  # Tracks the minimum value in the tree
        self.max_value = float('-inf')  # Tracks the maximum value in the tree
        self.sum_values = 0.0  # Tracks the sum of all inserted values
        self.count_values = 0  # Tracks the number of inserted values (nodes)
        self.mean_value = 0.0  # Tracks the mean value of all inserted data
        self.sum_of_squares = 0.0  # Tracks the sum of squares for variance calculation
        self.total_size = 0  # Tracks the total number of inserted elements (including duplicates)

    def insert(self, value: float):
        """
        Insert a value into the BST and update statistics.

        @param value: The trading price value to insert.
        """
        self.root = self._insert(self.root, value)  # Insert the new value into the tree
        self.last_inserted_value = value  # Update the last inserted value

        # Update statistics
        self.min_value = min(self.min_value, value)  # Update the minimum value
        self.max_value = max(self.max_value, value)  # Update the maximum value
        self.count_values += 1  # Increment the count of inserted values (excluding duplicates)
        self.sum_values += value  # Add the current value to the total sum
        self.total_size += 1  # Increment the total size for every insertion, including duplicates

        # Incrementally calculate the new mean
        old_mean = self.mean_value
        self.mean_value = self.sum_values / self.count_values

        # Update the sum of squares for variance calculation
        self.sum_of_squares += (value - old_mean) * (value - self.mean_value)

    def _insert(self, node: Node, value: float) -> Node:
        """
        Helper method to recursively insert a value into the BST.

        @param node: The current node being examined.
        @param value: The value to insert.
        @returns: The updated node after insertion.
        """
        if node is None:
            return Node(value)  # Create a new node when we find an insertion point

        if value < node.value:
            # If the value is less, go to the left subtree
            node.left = self._insert(node.left, value)
        elif value > node.value:
            # If the value is greater, go to the right subtree
            node.right = self._insert(node.right, value)
        else:
            # If the value already exists, increment the count for this node
            node.count += 1

        return node

    def get_all_values(self) -> List[float]:
        """
        Get all values stored in the BST in sorted order.

        @returns: A list of all values in the BST, sorted in ascending order.
        """
        values = []
        self._inorder_traversal(self.root, values)
        return values

    def _inorder_traversal(self, node: Node, values: List[float]):
        """
        Perform in-order traversal to gather all values from the BST.

        @param node: The current node in the tree.
        @param values: List to collect values in sorted order.
        """
        if node is None:
            return
        # Traverse the left subtree
        self._inorder_traversal(node.left, values)
        # Add the current node's value(s) to the list
        values.extend([node.value] * node.count)
        # Traverse the right subtree
        self._inorder_traversal(node.right, values)

    def get_stats(self) -> Dict[str, float or None]:
        """
        Get the current statistics (min, max, last, avg, var, size).

        @returns: A dictionary containing min, max, last, avg, var, and size.
        """
        if self.count_values == 0:
            # If the tree is empty, return None for all statistics
            return {
                "min": None,
                "max": None,
                "last": None,
                "avg": None,
                "var": None,
                "size": None
            }

        # Calculate variance as the sum of squares divided by the number of values
        variance = self.sum_of_squares / self.count_values if self.count_values > 1 else 0.0
        return {
            "min": self.min_value,
            "max": self.max_value,
            "last": self.last_inserted_value,
            "avg": self.mean_value,
            "var": variance,
            "size": self.total_size  # Total number of inserted elements
        }
