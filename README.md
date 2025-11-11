Project Overview

This project implements a price-time priority matching engine using a Red-Black Tree as the core data structure to store and manage price levels efficiently.
Each price level in the tree contains a FIFO queue of orders, ensuring that orders at the same price are matched based on earliest timestamp (time priority).

The system supports:

Placing Buy Orders

Placing Sell Orders

Automatic Trade Matching

Trade Recording and Logging

Efficient O(log n) Price Lookup / Insertion / Removal

1. Development Environment Setup
Step 1: Create Project Directory
mkdir orderbook-matching-engine
cd orderbook-matching-engine

Step 2: Create and Activate Virtual Environment
python3 -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

Step 3: Install Required Dependencies
pip install collections


(we only needed Python standard libraries: time, collections, etc.)

Step 4: Project File Structure
project-root/
│
├── rbtree.py          # Red-Black Tree implementation
├── orderbook.py       # Buy/Sell book operations + matching logic
├── main.py            # Runner + testing
└── README.md          # Documentation (this file)

2. Red-Black Tree Implementation
Node Structure

Each node represents a price level, not an individual order.

class Node:
    key   → price level
    value → list/deque of orders at this price
    color → RED/BLACK
    left/right/parent → pointers

Tree Initialization

A TNULL sentinel node is used to represent leaves.
The tree root initially points to this TNULL.

Insertion Process

New price inserted using standard BST insertion

Assigned RED color initially

fix_insert() is called to restore Red-Black Tree properties

Rotations + recoloring ensure:

No two consecutive red nodes

Balanced tree height

Root remains Black

This ensures O(log n) performance for:

Price search

Price level insertion

Price level deletion

3. Order Representation
class Order:
    price
    qty
    timestamp (to maintain FIFO)


Orders are not stored individually in the tree.
Instead, orders belonging to the same price level are stored in a FIFO list (deque).

This guarantees time-priority fairness at each price.

4. Buy and Sell Order Books

Two separate trees are maintained:

buy_book  → max-price priority (best bid is highest price)
sell_book → min-price priority (best ask is lowest price)


This allows efficient:

Best Bid lookup

Best Ask lookup

5. Matching Algorithm
Placing a Buy Order
place_buy(price, qty):


Compare buy price with best ask price.

If buy_price >= best_ask_price → Trade occurs.

Quantity matched based on minimum qty.

Update FIFO queue at the ask price.

If queue becomes empty → Remove the price node from tree.

If leftover quantity remains → Insert into buy tree price level.

Placing a Sell Order
place_sell(price, qty):


Same process but mirrored:

Compare sell price with best bid

Trade if sell_price <= best_bid_price

Insert leftover qty into sell tree

6. Trade Logging

Every executed trade is recorded:

{
 "price": traded_price,
 "qty": executed_quantity,
 "aggressor": BUY or SELL,
 "timestamp": time of execution
}


This enables:

Performance analysis

Backtesting

Replay of market events

7. Final Execution (main.py)

Example usage:

from orderbook import place_buy, place_sell, best_bid, best_ask

place_buy(100, 5)
place_sell(95, 3)
place_sell(100, 2)

print(best_bid())
print(best_ask())
print(trade_log)
