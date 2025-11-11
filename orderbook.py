from rbtree import RedBlackTree
from collections import deque
import time

class Order:
    def __init__(self, price, qty):
        self.price = price
        self.qty = qty
        self.timestamp = time.time()  # FIFO priority

buy_book = RedBlackTree()   # max-price priority
sell_book = RedBlackTree()  # min-price priority
trade_log = []              # store executed trades

def best_bid():
    node = buy_book.max_node()
    return (node.key, sum(node.value[i].qty for i in range(len(node.value)))) if node else (None, 0)

def best_ask():
    node = sell_book.min_node()
    return (node.key, sum(node.value[i].qty for i in range(len(node.value)))) if node else (None, 0)

def record_trade(price, qty, side):
    trade_log.append({"price": price, "qty": qty, "aggressor": side, "time": time.time()})

def place_buy(price, qty):
    global buy_book, sell_book
    order = Order(price, qty)

    # Match against best asks
    node = sell_book.root
    while node.key is not None and order.qty > 0 and order.price >= node.key:
        while node.value and order.qty > 0:
            best = node.value[0]
            trade_qty = min(order.qty, best.qty)
            order.qty -= trade_qty
            best.qty -= trade_qty
            record_trade(node.key, trade_qty, "BUY")

            if best.qty == 0:
                node.value.popleft()

        if not node.value:
            sell_book.delete(node.key)

        node = node.right

    # If leftover → insert into BUY book FIFO queue
    if order.qty > 0:
        n = buy_book.find(price) or buy_book.insert_price(price)
        n.value.append(order)

def place_sell(price, qty):
    global buy_book, sell_book
    order = Order(price, qty)

    # Match against best bids
    node = buy_book.root
    while node.key is not None and order.qty > 0 and order.price <= node.key:
        while node.value and order.qty > 0:
            best = node.value[0]
            trade_qty = min(order.qty, best.qty)
            order.qty -= trade_qty
            best.qty -= trade_qty
            record_trade(node.key, trade_qty, "SELL")

            if best.qty == 0:
                node.value.popleft()

        if not node.value:
            buy_book.delete(node.key)

        node = node.left

    # If leftover → insert into SELL book FIFO queue
    if order.qty > 0:
        n = sell_book.find(price) or sell_book.insert_price(price)
        n.value.append(order)
