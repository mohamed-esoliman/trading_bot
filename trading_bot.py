#!/usr/bin/env python3
# ~~~~~==============   HOW TO RUN   ==============~~~~~
# 1) Configure things in CONFIGURATION section
# 2) Change permissions: chmod +x bot.py
# 3) Run in loop: while true; do ./bot.py --test prod-like; sleep 1; done

import argparse
from collections import deque
from enum import Enum
import time
import socket
import json

# ~~~~~============== CONFIGURATION  ==============~~~~~
# Replace "REPLACEME" with your team name!
team_name = "PIKACHU"

# ~~~~~============== MAIN LOOP ==============~~~~~

# You should put your code here! We provide some starter code as an example,
# but feel free to change/remove/edit/update any of it as you'd like. If you
# have any questions about the starter code, or what to do next, please ask us!
#
# To help you get started, the sample code below tries to buy BOND for a low
# price, and it prints the current prices for VALE every second. The sample
# code is intended to be a working example, but it needs some improvement
# before it will start making good trades!


def main():
    args = parse_arguments()

    exchange = ExchangeConnection(args=args)
    state_manager = StateManager(exchange)
    # Store and print the "hello" message received from the exchange. This
    # contains useful information about your positions. Normally you start with
    # all positions at zero, but if you reconnect during a round, you might
    # have already bought/sold symbols and have non-zero positions.
    hello_message = exchange.read_message()
    state_manager.on_hello(hello_message)
    print("First message from exchange:", hello_message)

    # Send an order for BOND at a good price, but it is low enough that it is
    # unlikely it will be traded against. Maybe there is a better price to
    # pick? Also, you will need to send more orders over time.
    # exchange.send_add_message(order_id=1, symbol="BOND", dir=Dir.BUY, price=990, size=1)

    # Set up some variables to track the bid and ask price of a symbol. Right
    # now this doesn't track much information, but it's enough to get a sense
    # of the VALE market.
    # vale_bid_price, vale_ask_price = None, None
    # vale_last_print_time = time.time()

    # Here is the main loop of the program. It will continue to read and
    # process messages in a loop until a "close" message is received. You
    # should write to code handle more types of messages (and not just print
    # the message). Feel free to modify any of the starter code below.
    #
    # Note: a common mistake people make is to call write_message() at least
    # once for every read_message() response.
    #
    # Every message sent to the exchange generates at least one response
    # message. Sending a message in response to every exchange message will
    # cause a feedback loop where your bot's messages will quickly be
    # rate-limited and ignored. Please, don't do that!

    def exchange_bonds():
        bonds_position = state_manager.positions["BOND"]

        buying_order = Order(
            state_manager.next_id(), "BOND", Dir.BUY, 999, 100 - bonds_position
        )
        selling_order = Order(
            state_manager.next_id(), "BOND", Dir.SELL, 1001, abs(-100 - bonds_position)
        )

        def buy_bonds():
            if bonds_position < 100:
                buying_order.send(exchange)
                state_manager.open_orders[buying_order.id_] = buying_order

        def sell_bonds():
            if bonds_position > -100:
                selling_order.send(exchange)
                state_manager.open_orders[selling_order.id_] = selling_order

        buy_bonds()
        sell_bonds()

    # initializing the bond buying
    bonds_position = state_manager.positions["BOND"]

    buying_order = Order(
        state_manager.next_id(), "BOND", Dir.BUY, 999, 100 - bonds_position
    )
    selling_order = Order(
        state_manager.next_id(), "BOND", Dir.SELL, 1001, abs(-100 - bonds_position)
    )

    buying_order.send(exchange)
    selling_order.send(exchange)

    state_manager.open_orders[buying_order.id_] = buying_order
    state_manager.open_orders[selling_order.id_] = selling_order

    # VALES
    vale_bid_price, vale_ask_price = None, None
    vale_last_print_time = time.time()

    valbz_bid_price, vale_ask_price = None, None
    valbz_last_print_time = time.time()

    # XLF
    gs_bid_price, gs_ask_price = None, None
    gs_last_print_time = time.time()

    ms_bid_price, ms_ask_price = None, None
    ms_last_print_time = time.time()

    wfc_bid_price, wfc_ask_price = None, None
    wfc_last_print_time = time.time()

    xlf_bid_price, xlf_ask_price = None, None
    xlf_last_print_time = time.time()

    while True:
        message = exchange.read_message()

        # Some of the message types below happen infrequently and contain
        # important information to help you understand what your bot is doing,
        # so they are printed in full. We recommend not always printing every
        # message because it can be a lot of information to read. Instead, let
        # your code handle the messages and just print the information
        # important for you!

        if message["type"] == "close":
            print("The round has ended")
            break
        elif message["type"] == "error":
            print(message)
        elif message["type"] == "reject":
            print(message)
        elif message["type"] == "fill":
            for order_key in state_manager.open_orders:
                exchange.send_cancel_message(order_key)

            if message["symbol"] == "BOND":
                if message["dir"] == "BUY":
                    state_manager.positions["BOND"] += message["size"]
                else:
                    state_manager.positions["BOND"] -= message["size"]
                exchange_bonds()

            if message["symbol"] == "VALE":
                state_manager.positions["VALE"] += 1

            if message["symbol"] == "VALBZ":
                state_manager.positions["VALE"] -= 1

            print(message)
            print(state_manager.positions)

        elif message["type"] == "book":
            if message["symbol"] == "VALBZ":

                def best_price(side):
                    if message[side]:
                        return message[side][0][0]

                valbz_bid_price = best_price("buy")
                valbz_ask_price = best_price("sell")

                now = time.time()

                if now > valbz_last_print_time + 1:
                    valbz_last_print_time = now
                    # print(
                    #     {
                    #         "valbz_bid_price": valbz_bid_price,
                    #         "valbz_ask_price": valbz_ask_price,
                    #     }
                    # )

            elif message["symbol"] == "VALE":

                def best_price(side):
                    if message[side]:
                        return message[side][0][0]

                vale_bid_price = best_price("buy")
                vale_ask_price = best_price("sell")

                if valbz_bid_price is not None and vale_ask_price is not None:

                    if vale_ask_price + 10 < valbz_bid_price:
                        buying_order = Order(
                            state_manager.next_id(), "VALE", Dir.BUY, vale_ask_price, 1
                        )
                        buying_order.send(exchange)
                        state_manager.open_orders[buying_order.id_] = buying_order

                        exchange.send_convert_message(
                            state_manager.next_id(), "VALE", Dir.SELL, 1
                        )

                        selling_order = Order(
                            state_manager.next_id(),
                            "VALBZ",
                            Dir.SELL,
                            valbz_bid_price,
                            1,
                        )
                        selling_order.send(exchange)
                        state_manager.open_orders[selling_order.id_] = selling_order

            elif message["symbol"] == "GS":

                def best_price(side):
                    if message[side]:
                        return message[side][0][0]

                gs_bid_price = best_price("buy")
                gs_ask_price = best_price("sell")

                now = time.time()

                if now > gs_last_print_time + 1:
                    gs_last_print_time = now

            elif message["symbol"] == "MS":

                def best_price(side):
                    if message[side]:
                        return message[side][0][0]

                ms_bid_price = best_price("buy")
                ms_ask_price = best_price("sell")

                now = time.time()

                if now > ms_last_print_time + 1:
                    ms_last_print_time = now

            elif message["symbol"] == "WFC":

                def best_price(side):
                    if message[side]:
                        return message[side][0][0]

                wfc_bid_price = best_price("buy")
                wfc_ask_price = best_price("sell")

                now = time.time()

                if now > wfc_last_print_time + 1:
                    wfc_last_print_time = now

            elif message["symbol"] == "XLF":

                def best_price(side):
                    if message[side]:
                        return message[side][0][0]

                xlf_bid_price = best_price("buy")
                xlf_ask_price = best_price("sell")

                if (
                    xlf_bid_price is not None
                    and ms_ask_price is not None
                    and gs_ask_price is not None
                    and wfc_ask_price is not None
                ):

                    if (
                        2 * gs_ask_price + 3 * ms_ask_price + 2 * wfc_ask_price
                    ) + 3010 < xlf_bid_price:
                        buying_order1 = Order(
                            state_manager.next_id(), "GS", Dir.BUY, gs_ask_price, 2
                        )
                        buying_order1.send(exchange)
                        state_manager.open_orders[buying_order1.id_] = buying_order1

                        buying_order2 = Order(
                            state_manager.next_id(), "MS", Dir.BUY, ms_ask_price, 3
                        )
                        buying_order2.send(exchange)
                        state_manager.open_orders[buying_order2.id_] = buying_order2

                        buying_order3 = Order(
                            state_manager.next_id(), "WFC", Dir.BUY, wfc_ask_price, 2
                        )
                        buying_order3.send(exchange)
                        state_manager.open_orders[buying_order3.id_] = buying_order3

                        buying_order4 = Order(
                            state_manager.next_id(), "BOND", Dir.BUY, 999, 2
                        )
                        buying_order4.send(exchange)
                        state_manager.open_orders[buying_order4.id_] = buying_order4

                        exchange.send_convert_message(
                            state_manager.next_id(), "XLF", Dir.BUY, 1
                        )

                        selling_order = Order(
                            state_manager.next_id(), "XLF", Dir.SELL, xlf_bid_price, 1
                        )
                        selling_order.send(exchange)
                        state_manager.open_orders[selling_order.id_] = selling_order


class Order:
    def __init__(self, id_, symbol, dir_, price, size):
        self.id_ = id_
        self.symbol = symbol
        self.dir_ = dir_
        self.price = price
        self.size = size

    def __str__(self):
        return (
            f"Id {self.id_}: {self.dir_} {self.size} of {self.symbol} for ${self.price}"
        )

    def send(self, exchange):
        exchange.send_add_message(
            order_id=self.id_,
            symbol=self.symbol,
            dir=self.dir_,
            price=self.price,
            size=self.size,
        )


class StateManager:
    def __init__(self, exchange):
        self.exchange = exchange
        self.positions = {}
        self.open_orders = {}
        # Start ids at -1 because we always increment when getting the next ID
        self.cur_id = -1

    def next_id(self):
        self.cur_id += 1
        return self.cur_id

    def new_order(self, symbol, dir_, price, size):
        """Sends a new order and keeps track of it in our state"""
        order_id = self.next_id()
        order = Order(order_id, symbol, dir_, price, size)
        print(f"Sending order {order}")
        order.send(self.exchange)

    def on_hello(self, hello_message):
        """Handle a hello message by setting our current positions"""
        symbol_positions = hello_message["symbols"]
        for symbol_position in symbol_positions:
            symbol = symbol_position["symbol"]
            position = symbol_position["position"]
            self.positions[symbol] = position
        print(self.positions)

    def on_ack(self, message):
        """Handle an ack by marking the order as live"""
        # TODO
        pass

    def on_fill(self, message):
        """Handle a fill by decrementing the open size of the order and updating our
        positions"""
        # TODO
        pass


# ~~~~~============== PROVIDED CODE ==============~~~~~

# You probably don't need to edit anything below this line, but feel free to
# ask if you have any questions about what it is doing or how it works. If you
# do need to change anything below this line, please feel free to


class Dir(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class ExchangeConnection:
    def __init__(self, args):
        self.message_timestamps = deque(maxlen=500)
        self.exchange_hostname = args.exchange_hostname
        self.port = args.port
        exchange_socket = self._connect(add_socket_timeout=args.add_socket_timeout)
        self.reader = exchange_socket.makefile("r", 1)
        self.writer = exchange_socket

        self._write_message({"type": "hello", "team": team_name.upper()})

    def read_message(self):
        """Read a single message from the exchange"""
        message = json.loads(self.reader.readline())
        if "dir" in message:
            message["dir"] = Dir(message["dir"])
        return message

    def send_add_message(
        self, order_id: int, symbol: str, dir: Dir, price: int, size: int
    ):
        """Add a new order"""
        self._write_message(
            {
                "type": "add",
                "order_id": order_id,
                "symbol": symbol,
                "dir": dir,
                "price": price,
                "size": size,
            }
        )

    def send_convert_message(self, order_id: int, symbol: str, dir: Dir, size: int):
        """Convert between related symbols"""
        self._write_message(
            {
                "type": "convert",
                "order_id": order_id,
                "symbol": symbol,
                "dir": dir,
                "size": size,
            }
        )

    def send_cancel_message(self, order_id: int):
        """Cancel an existing order"""
        self._write_message({"type": "cancel", "order_id": order_id})

    def _connect(self, add_socket_timeout):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if add_socket_timeout:
            # Automatically raise an exception if no data has been recieved for
            # multiple seconds. This should not be enabled on an "empty" test
            # exchange.
            s.settimeout(5)
        s.connect((self.exchange_hostname, self.port))
        return s

    def _write_message(self, message):
        what_to_write = json.dumps(message)
        if not what_to_write.endswith("\n"):
            what_to_write = what_to_write + "\n"

        length_to_send = len(what_to_write)
        total_sent = 0
        while total_sent < length_to_send:
            sent_this_time = self.writer.send(
                what_to_write[total_sent:].encode("utf-8")
            )
            if sent_this_time == 0:
                raise Exception("Unable to send data to exchange")
            total_sent += sent_this_time

        now = time.time()
        self.message_timestamps.append(now)
        if len(
            self.message_timestamps
        ) == self.message_timestamps.maxlen and self.message_timestamps[0] > (now - 1):
            print(
                "WARNING: You are sending messages too frequently. The exchange will start ignoring your messages. Make sure you are not sending a message in response to every exchange message."
            )


def parse_arguments():
    test_exchange_port_offsets = {"prod-like": 0, "slower": 1, "empty": 2}

    parser = argparse.ArgumentParser(description="Trade on an ETC exchange!")
    exchange_address_group = parser.add_mutually_exclusive_group(required=True)
    exchange_address_group.add_argument(
        "--production", action="store_true", help="Connect to the production exchange."
    )
    exchange_address_group.add_argument(
        "--test",
        type=str,
        choices=test_exchange_port_offsets.keys(),
        help="Connect to a test exchange.",
    )

    # Connect to a specific host. This is only intended to be used for debugging.
    exchange_address_group.add_argument(
        "--specific-address", type=str, metavar="HOST:PORT", help=argparse.SUPPRESS
    )

    args = parser.parse_args()
    args.add_socket_timeout = True

    if args.production:
        args.exchange_hostname = "production"
        args.port = 25000
    elif args.test:
        args.exchange_hostname = "test-exch-" + team_name
        args.port = 25000 + test_exchange_port_offsets[args.test]
        if args.test == "empty":
            args.add_socket_timeout = False
    elif args.specific_address:
        args.exchange_hostname, port = args.specific_address.split(":")
        args.port = int(port)

    return args


if __name__ == "__main__":
    # Check that [team_name] has been updated.
    assert (
        team_name == "PIKACHU"
    ), "Please put your team name in the variable [team_name]."

    main()
