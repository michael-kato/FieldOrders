"""
To create financial independence and free myself
"""

import os
import sys
import time
import json
import datetime
import schedule
import itertools
import importlib


import mpmath as mp
sys.path.append(os.path.dirname(__file__) + "\\kucoin\\")
import kucoin.client as kucoin
importlib.reload(kucoin)

"""
TODO:
Refresh once a minute
get all markets


START DOWNLOADING ALL PRICE ACTION
KEEP LOCAL COPY of 1hr data
"""

class ChartHistory(object):
    def __init__(self):
        pass

class dobj(object):
    """
    Lets you use dict keys as object attributes
    kinda cool, but mostly just confusing in practice
    """
    def __init__(self, d):
        self.__dict__ = d

    def __iter__(self):
        for attr, value in self.__dict__.items():
            yield attr, value

class FieldOrder():
    """
    The ultimate trading tool (once it's finished). Fat finger catcher, always profit taking, always rebuying with confidence of an eventual return to base. Thanks Luc!
    """
    def __init__(self):
        # BOT

        # never change these...
        self.base_currency = "USDT"
        PUB = "5e4a22d29a8f450008d86f51"
        SEC = "6e2a49f0-5d86-45cf-a638-7e29fb561090"
        TRADING = "tthis_willbethebestBot15!"
        # /never change these...

        self.api = kucoin.Client(PUB, SEC, TRADING)

        self.data_file = os.path.dirname(__file__) + "{}_data.json".format(self.base_currency)

        self.json = json.load(self.data_file)
        # BIG object that has all the data we really need
        self.data = json.load(self.data_file)

        #quantityIncrement = mp.mpf( symbolData['quantityIncrement'] )
        #tickSize = mp.mpf( symbolData['tickSize'] )

         # bot should never have a blance of more than this, send an email every day we exceed it
        self.maxCapital = 10000

        # get wanted pairs and wanted data
        self.get_pairs()
        # start the business
        self.manage_orders()

    def get_usdt_pairs(self):
        """
        Gets all the SHITCOIN/USDT trading pairs and any additional information the bot might need
        """
        usdt_pairs = {}
        raw_symbols = self.api.get_symbols()
        '''
        {'symbol': 'GRIN-USDT', 'quoteMaxSize': '99999999', 'enableTrading': True, 'priceIncrement': '0.000001',
        'feeCurrency': 'USDT', 'baseMaxSize': '10000000000', 'baseCurrency': 'GRIN', 'quoteCurrency': 'USDT', 'market': 'USDS', 'quoteIncrement': '0.000001',
        'baseMinSize': '0.01', 'quoteMinSize': '0.01', 'name': 'GRIN-USDT', 'baseIncrement': '0.00000001', 'isMarginEnabled': False}
        '''
        for data in raw_symbols:
            if self.base_currency in data["symbol"]:
                pair = data["symbol"]
                quote, base = pair.split('-')
                if base == self.base_currency:
                    # add/modify data here
                    usdt_pairs[quote] = data

        return usdt_pairs

    def get_pairs(self):
        self.usdt_pairs = self.get_usdt_pairs()
        print("Got data for {} pairs".format(len(self.usdt_pairs)))

    def manage_orders(self):
        """
        Goes through all open orders on pair, figured out if they're in range, wipe and recreate if adjustment is needed
        def get_orders(self, symbol=None, status=None, side=None, order_type=None, start=None, end=None, page=None, limit=None):
        """
        for coin, pair_info in self.usdt_pairs.items():
            orders = self.api.get_orders(pair_info["symbol"], status="active")
            print(coin, orders["totalNum"])
            if orders["totalNum"]:
                print(len(orders["items"]))
                for order in orders["items"]:
                    print(order)

                    print(mp.mpf())

                # ticker = current price action, bid/ask, etc
                ticker = self.api.get_ticker(pair_info["symbol"])
                print(ticker)
                return

if __name__ == "__main__":
    order = FieldOrder()

    # the rest on a timer
    schedule.every(1).days.do(order.get_pairs)
    schedule.every(1).minutes.do(order.manage_orders)
