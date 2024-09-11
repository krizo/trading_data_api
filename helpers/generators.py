import random
import string


class SymbolGenerator:
    _generated_symbols = []

    def __init__(self, length: int = 4):
        self.length = length

    def __next__(self):
        return self._generate_symbol()

    def _generate_symbol(self):
        while True:
            symbol = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(self.length))
            if symbol not in self._generated_symbols:
                return symbol
