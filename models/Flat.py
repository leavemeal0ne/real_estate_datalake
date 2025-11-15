class Flat:
    def __init__(self, price=None):
        if price is None:
            self.price = 0
            return
        self.price = price