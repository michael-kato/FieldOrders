"""
Experiment to see if I can always buy and always sell perfect tops and perfect bottoms
Take 100% advantage of volatility. Trade any volitile chart with an overwhelming number of orders.
"""

import os
import sys
import time
import json
import logger
import datetime as dt
import schedule
import itertools
import importlib
#import dateparser

import mpmath as mp
sys.path.append(os.path.dirname(__file__) + "\\kucoin\\")
from kucoin.client import Client as kucoin
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

        self.now = dt.datetime.now().strftime("[(%y/%Y – Year), (%a/%A- weekday), (%b/%B- month), (%d - day of month)] . ")
        print(self.now)
        return

        # never change these...
        self.base_currency = "USDT"
        self.exclude = ["TUSD"]
        PUB = "5e4a22d29a8f450008d86f51"
        SEC = "6e2a49f0-5d86-45cf-a638-7e29fb561090"
        TRADING = "tthis_willbethebestBot15!"
        # /never change these...

        self.kc = kucoin(PUB, SEC, TRADING)

        self.log_file = open(os.path.dirname(__file__) + "\\{}.log".format(self.base_currency), 'a+')
        self.data_file = os.path.dirname(__file__) + "\\{}_data.json".format(self.base_currency)

        self.global_time = ()

        # get currencies
        #currencies = self.api.get_currencies()
        # get market depth
        depth = self.kc.get_order_book('KCS-BTC')

        # get symbol klines
        klines = self.kc.get_kline_data('KCS-BTC')

        # get list of markets
        markets = self.kc.get_markets()

        # place a market buy order
        #order = self.api.create_market_order('NEO', kucoin.SIDE_BUY, size=20)

        # get list of active orders
        #orders = self.api.get_active_orders('KCS-BTC')

        self.log(depth)
        self.log(klines)
        self.log(markets)

        # BIG object that has all the data we really need
        self.data = self.open_json(self.data_file)
        #quantityIncrement = mp.mpf( symbolData['quantityIncrement'] )
        #tickSize = mp.mpf( symbolData['tickSize'] )

         # bot should ideally have a "capital" value of 50% the account value
        self.capital = 350
        self.orders_per_chart = 30
        # get wanted pairs and wanted data
        """
        {'symbol': 'TIME-ETH', 'quoteMaxSize': '99999999', 'enableTrading': True,
        'priceIncrement': '0.0000001', 'feeCurrency': 'ETH', 'baseMaxSize': '10000000000',
        'baseCurrency': 'TIME', 'quoteCurrency': 'ETH', 'market': 'ALTS',
        'quoteIncrement': '0.0000001', 'baseMinSize': '0.01', 'quoteMinSize': '0.0001',
        'name': 'TIME-ETH', 'baseIncrement': '0.000001', 'isMarginEnabled': False}
        """
        self.usdt_pairs = self.get_pairs()
        self.num_pairs = len(self.usdt_pairs)

        self.accounts = self.get_accounts()
        #self.charts = self.get_charts()



        self.field_buy("XLM-USDT")
        self.field_sell("XLM-USDT")



        # start the business
        self.manage_orders()

    def log(self, *message):
        # THIS IS THE ONLY PRINT ALLOWED IN THE PROGRAM, YA HOSER
        print(message)
        for msg in message:
            self.log_file.write(str(msg) + '\n')
        self.save_json(message)

    def open_json(self):
        if not os.path.isfile( self.log_file):
            with open( self.log_file, 'w+') as df:
                return json.load(df)
        else:
            with open( self.log_file, 'r') as df:
                return json.load(df)

    def save_json(self, data):
        json.dump(data,  self.log_file)

    def date_to_seconds(self, date_str):
        """Convert UTC date to seconds

        If using offset strings add "UTC" to date string e.g. "now UTC", "11 hours ago UTC"

        See dateparse docs for formats http://dateparser.readthedocs.io/en/latest/

        :param date_str: date in readable format, i.e. "January 01, 2018", "11 hours ago UTC", "now UTC"
        :type date_str: str
        """
        # get epoch value in UTC
        epoch = datetime.datetime.utcfromtimestamp(0).replace(tzinfo=pytz.utc)
        # parse our date string
        d = dateparser.parse(date_str)
        # if the date is not timezone aware apply UTC timezone
        if d.tzinfo is None or d.tzinfo.utcoffset(d) is None:
            d = d.replace(tzinfo=pytz.utc)

        # return the difference in time
        return int((d - epoch).total_seconds())

    def get_balance(self):
        balance = {}


    def get_accounts(self):
        self.accounts = [account for account in self.kucoin.get_accounts()]
        self.account_ids = [account["id"] for account in self.accounts]
        #for account_ids in self.account_ids:
        #    self.log(account_ids)
        #for account in self.accounts:
        #    self.log(account)
        #    self.log(self.api.get_account(account["id"]))

        return self.accounts

    def get_historical_klines(self, symbol, interval, start_str, end_str=None):
        """
        # fetch 1 minute klines for the last day up until now
        klines = get_historical_klines_tv("KCS-BTC", "1", "1 day ago UTC")

        # fetch 30 minute klines for the last month of 2017
        klines = get_historical_klines_tv("NEO-BTC", "30", "1 Dec, 2017", "1 Jan, 2018")

        # fetch weekly klines since it listed
        klines = get_historical_klines_tv("XRP-BTC", "W", "1 Jan, 2017")

        Get Historical Klines from Kucoin (Trading View)

        See dateparse docs for valid start and end string formats http://dateparser.readthedocs.io/en/latest/

        If using offset strings for dates add "UTC" to date string e.g. "now UTC", "11 hours ago UTC"

        :param symbol: Name of symbol pair e.g BNBBTC
        :type symbol: str
        :param interval: Trading View Kline interval
        :type interval: str
        :param start_str: Start date string in UTC format
        :type start_str: str
        :param end_str: optional - end date string in UTC format
        :type end_str: str

        :return: list of OHLCV values

        """

        # init our array for klines
        klines = []

        # convert our date strings to seconds
        start_ts = self.date_to_seconds(start_str)

        # if an end time was not passed we need to use now
        if end_str is None:
            end_str = 'now UTC'
        end_ts = self.date_to_seconds(end_str)

        kline_res = self.kc.get_kline_data(symbol, interval, start_ts, end_ts)

        self.log(kline_res)

        # check if we got a result
        if 't' in kline_res and len(kline_res['t']):
            # now convert this array to OHLCV format and add to the array
            for i in range(1, len(kline_res['t'])):
                klines.append((
                    kline_res['t'][i],
                    kline_res['o'][i],
                    kline_res['h'][i],
                    kline_res['l'][i],
                    kline_res['c'][i],
                    kline_res['v'][i]
                ))

        # finally return our converted klines
        return klines

    def save_klines(self):


        symbol = "KCS-BTC"
        start = "1 Dec, 2017"
        end = "1 Jan, 2018"
        interval = "1hour"

        klines = self.get_historical_klines(symbol, interval, start, end)

        # open a file with filename including symbol, interval and start and end converted to seconds
        with open("Kucoin_{}_{}_{}-{}.json".format(symbol, interval,self.date_to_seconds(start), self.date_to_seconds(end)), 'w+') \
            as f: f.write(json.dumps(klines))

    def field_buy(self, symbol):
        """
        Get current price
        Get current orders on chart
        If price is too close to highest order, remove order
        Insert a duplicate order randomly
        """

        end_percent = 150
        current_price = 15#self.get_price()
        self.log(current_price)
        buys = {}
        new_price = current_price * 1.05
        while (new_price / current_price) > 150:
            self.log("New sell at: {}".format(new_price))
            new_price *= 1.05

        self.log(buys)

        return buys

    def field_sell(self, symbol):
        symbol = "XLM-USDT"
        size = 10
        current_price = 0.01

        sells = {}
        new_price = current_price * 0.95
        while (new_price / current_price) > 0.05:
            #order = self.api.create_limit_order(self, symbol, "SELL", new_price, size)
            self.log("New buy at: {}".format(new_price))
            new_price *= 0.95

        return sells

    def set_min_buy(self):
        """
        Some rules:
            We use ~50% of capital at any given time
            We set ~30 orders per chart
            Currently have about 79 USDT trading pairs
        """

    def get_price_history(self):
        trade_history = self.kc.get_trade_histories()
        for trade in trade_history:
            self.log(trade)

    def get_usdt_pairs(self):
        """
        Gets all the SHITCOIN/USDT trading pairs and any additional information the bot might need
        """
        usdt_pairs = {}
        raw_symbols = self.kc.get_symbols()
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
                    self.log(pair, quote)
                    # add/modify data here
                    usdt_pairs[quote] = data

        return usdt_pairs

    def get_pairs(self):
        usdt_pairs = self.get_usdt_pairs()
        self.log("Got data for {} pairs".format(len(usdt_pairs)))
        return usdt_pairs

    def manage_orders(self):
        """
        Goes through all open orders on pair, figured out if they're in range, wipe and recreate if adjustment is needed
        def get_orders(self, symbol=None, status=None, side=None, order_type=None, start=None, end=None, page=None, limit=None):
        """
        for coin, pair_info in self.usdt_pairs.items():
            orders = self.kc.get_orders(pair_info["symbol"], status="active")
            self.log(coin, orders["totalNum"])
            if orders["totalNum"]:
                self.log(len(orders["items"]))
                for order in orders["items"]:
                    self.log(order)

                    self.log(mp.mpf())

                # ticker = current price action, bid/ask, etc
                ticker = self.kc.get_ticker(pair_info["symbol"])
                self.log(ticker)
                return

if __name__ == "__main__":
    order = FieldOrder()

    # the rest on a timer
    schedule.every(1).days.do(order.get_pairs)
    schedule.every(1).minutes.do(order.manage_orders)


"""
import asyncio

from kucoin.client import Client
from kucoin.asyncio import KucoinSocketManager

api_key = '<api_key>'
api_secret = '<api_secret>'
api_passphrase = '<api_passphrase>'


async def main():
    global loop

    # callback function that receives messages from the socket
    async def handle_evt(msg):
        if msg['topic'] == '/market/ticker:ETH-USDT':
            print(f'got ETH-USDT tick:{msg["data"]}')

        elif msg['topic'] == '/market/snapshot:BTC':
            print(f'got BTC market snapshot:{msg["data"]}')

        elif msg['topic'] == '/market/snapshot:KCS-BTC':
            print(f'got KCS-BTC symbol snapshot:{msg["data"]}')

        elif msg['topic'] == '/market/ticker:all':
            print(f'got all market snapshot:{msg["data"]}')

        elif msg['topic'] == '/account/balance':
            print(f'got account balance:{msg["data"]}')

        elif msg['topic'] == '/market/level2:KCS-BTC':
            print(f'got L2 msg:{msg["data"]}')

        elif msg['topic'] == '/market/match:BTC-USDT':
            print(f'got market match msg:{msg["data"]}')

        elif msg['topic'] == '/market/level3:BTC-USDT':
            if msg['subject'] == 'trade.l3received':
                if msg['data']['type'] == 'activated':
                    # must be logged into see these messages
                    print(f"L3 your order activated: {msg['data']}")
                else:
                    print(f"L3 order received:{msg['data']}")
            elif msg['subject'] == 'trade.l3open':
                print(f"L3 order open: {msg['data']}")
            elif msg['subject'] == 'trade.l3done':
                print(f"L3 order done: {msg['data']}")
            elif msg['subject'] == 'trade.l3match':
                print(f"L3 order matched: {msg['data']}")
            elif msg['subject'] == 'trade.l3change':
                print(f"L3 order changed: {msg['data']}")

    client = kucoin(api_key, api_secret, api_passphrase)

    ksm = await KucoinSocketManager.create(loop, client, handle_evt)

    # Note: try these one at a time, if all are on you will see a lot of output

    # ETH-USDT Market Ticker
    await ksm.subscribe('/market/ticker:ETH-USDT')
    # BTC Symbol Snapshots
    await ksm.subscribe('/market/snapshot:BTC')
    # KCS-BTC Market Snapshots
    await ksm.subscribe('/market/snapshot:KCS-BTC')
    # All tickers
    await ksm.subscribe('/market/ticker:all')
    # Level 2 Market Data
    await ksm.subscribe('/market/level2:KCS-BTC')
    # Market Execution Data
    await ksm.subscribe('/market/match:BTC-USDT')
    # Level 3 market data
    await ksm.subscribe('/market/level3:BTC-USDT')
    # Account balance - must be authenticated
    await ksm.subscribe('/account/balance')

    while True:
        print("sleeping to keep loop open")
        await asyncio.sleep(20, loop=loop)


if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
"""