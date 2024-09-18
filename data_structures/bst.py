class Node:
    def __init__(self, value: float):
        """
        Initialize a new Node in the BST.

        Args:
            value (float): The trading price value to store in the node.
        """
        self.value = value
        self.left = None  # Left child node
        self.right = None  # Right child node
        self.count = 1  # Number of occurrences of this value
        self.size = 1  # Size of the subtree (number of nodes including itself)

class BST:
    def __init__(self):
        """
        Initialize an empty Binary Search Tree.
        """
        self.root = None
        self.last_inserted_value = None  # Keeps track of the last inserted value

    def insert(self, value: float):
        """
        Insert a value into the BST and update the size and last inserted value.

        Args:
            value (float): The trading price value to insert.
        """
        self.root = self._insert(self.root, value)
        self.last_inserted_value = value  # Track the last inserted value

    def _insert(self, node: Node, value: float) -> Node:
        """
        Helper method to recursively insert a value into the BST.

        Args:
            node (Node): The current node being examined.
            value (float): The value to insert.

        Returns:
            Node: The updated node after insertion.
        """
        if node is None:
            return Node(value)

        if value < node.value:
            node.left = self._insert(node.left, value)
        elif value > node.value:
            node.right = self._insert(node.right, value)
        else:
            node.count += 1  # Handle duplicate values

        # Update the size of the current node's subtree
        node.size = node.count + (node.left.size if node.left else 0) + (node.right.size if node.right else 0)
        return node

    def get_min(self) -> float:
        """
        Get the minimum value stored in the BST.

        Returns:
            float: The minimum trading price in the tree.
        """
        return self._min_value(self.root)

    def _min_value(self, node: Node) -> float:
        """
        Helper method to find the minimum value in a subtree.

        Args:
            node (Node): The root node of the subtree.

        Returns:
            float: The minimum value in the subtree.
        """
        while node.left:
            node = node.left
        return node.value

    def get_max(self) -> float:
        """
        Get the maximum value stored in the BST.

        Returns:
            float: The maximum trading price in the tree.
        """
        return self._max_value(self.root)

    def _max_value(self, node: Node) -> float:
        """
        Helper method to find the maximum value in a subtree.

        Args:
            node (Node): The root node of the subtree.

        Returns:
            float: The maximum value in the subtree.
        """
        while node.right:
            node = node.right
        return node.value

    def get_last(self) -> float:
        """
        Get the most recent value inserted into the BST (not necessarily sorted).

        Returns:
            float: The most recent trading price.
        """
        return self.last_inserted_value

    def get_size(self) -> int:
        """
        Get the total number of elements in the BST.

        Returns:
            int: The total number of elements in the tree.
        """
        return self._get_size(self.root)

    def _get_size(self, node: Node) -> int:
        """
        Helper method to get the size of the subtree.

        Args:
            node (Node): The root node of the subtree.

        Returns:
            int: The size of the subtree rooted at the node.
        """
        return node.size if node else 0

    def inorder(self) -> list:
        """
        Perform an in-order traversal of the BST and return a sorted list of values.

        Returns:
            list: A list of trading prices sorted in ascending order.
        """
        result = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node: Node, result: list):
        """
        Helper method to perform in-order traversal of the BST.

        Args:
            node (Node): The current node being visited.
            result (list): The list to append values to.
        """
        if not node:
            return
        self._inorder(node.left, result)
        result.extend([node.value] * node.count)  # Handle duplicate values
        self._inorder(node.right, result)

    def get_k_values(self, k: int) -> list:
        """
        Retrieve the last 'k' values from the BST in ascending order.

        Args:
            k (int): The number of values to retrieve.

        Returns:
            list: A list of the most recent 'k' trading prices.
        """
        inorder_values = self.inorder()
        return inorder_values[-k:]

    def calculate_avg_and_var(self, k: int) -> tuple:
        """
        Calculate the average and variance of the last 'k' values in the BST.

        Args:
            k (int): The number of values to consider.

        Returns:
            tuple: A tuple containing the average and variance of the last 'k' trading prices.
        """
        values = self.get_k_values(k)
        avg_value = sum(values) / len(values)
        var_value = sum((x - avg_value) ** 2 for x in values) / len(values)
        return avg_value, var_value
