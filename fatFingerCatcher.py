# condenses recent price action into a line, measures strong variation from that line
# then places range orders through the average variation
'''
First, get current coin balances. We want to never own any coin except the trading pair.
This should be a fresh account, used only for bot trading.
If there is a balance, somehow figure out what the buy price was and what the current bid is
Sell place a sell order at the current bid, if that is over 10% of the buy spot
Alternatively we can use an average of the last 5 minutes of price action maybe -5% or something
Send text and email when a buy order is hit. Very important.

All buy orders should be the same size, ranging from PRICE_BUFFER, to the average FF amount
Remove nearest order to the current price when current price starts dropping too much (-5%)

Everything is Decimals
'''

# for emails
import smtplib
import email

import time
import uuid

import decimal

BUY_FAT_FINGERS = ['ART', 'AVH', 'AXP', 'PRG']
SELL_FAT_FINGERS = ['CLOAK', 'PRG']


def get_min_order_amount():
    """
    Calculate how much capital to use in each buy order based on
        The number of coins to set orders on,
        The total amount of trading capital you have for use in the account
        The number of buy orders you want to place
        Probably some other stuff
    """
    pass

def get_sma(coin):
    """
    Get current simple moving average so we can determine where to sell after a fat finger
    Always uses 1 minute average in order to hug the price trend as tight as possible <3
    """
    pass

def set_orders(coin):
    ff_data = get_fat_fingers(coin)
    print(ff_data)

def get_capital_balance(trading_pair):
    pass

def get_coin_balance(coin):
    pass

def get_recent_orders(coin, minutes):
    recent_orders = 1 # TODO API
    return recent_orders

def dump_coin(coin):
    average_price = get_sma(coin)
    # TODO API, set sell order at SMA price

def cancelOrders(coin):
    if coin:
        print("Cancelling orders for", coin)
        # API TODO
    else:
        print("Cancelling all orders for all coins in COIN_LIST")
        # API TODO

def main():
    api = HitBTC()

    btc_usd = api.get_symbol('BTCUSD')
    address = api.get_address('BTC')     # get BTC address for deposit

    print("Symbol:", btc_usd)
    print('BTC deposit address:', address)

    # get BTC trading balance
    btc_balance = 0.0
    balances = api.get_trading_balance()
    for balance in balances:
        balance_amount = float(balance['available'])
        if balance_amount > 0: print(balance)
        if balance['currency'] == 'BTC':
            btc_balance = balance_amount

    print('Current BTC balance: %s' % btc_balance)

    # sell eth at the best price
    if btc_balance >= float(btc_usd['quantityIncrement']):
        client_order_id = uuid.uuid4().hex
        #orderbook = api.get_orderbook('BTC')
        # set price a little high
        #best_price = decimal.Decimal(orderbook['bid'][0]['price']) + decimal.Decimal(btc_usd['tickSize'])

        #print("Current best price is: %s" % best_price)
        '''
        order = api.new_order(client_order_id, 'BTCUSD', 'sell', btc_balance, best_price)
        if 'error' not in order:
            if order['status'] == 'filled':
                print("Order filled", order)
            elif order['status'] == 'new' or order['status'] == 'partiallyFilled':
                print("Waiting order...")
                for k in range(0, 3):
                    order = api.get_order(client_order_id, 20000)
                    print(order)

                    if 'error' in order or ('status' in order and order['status'] == 'filled'):
                        break

                # cancel order if it isn't filled
                if 'status' in order and order['status'] != 'filled':
                    cancel = api.cancel_order(client_order_id)
                    print('Cancel order result', cancel)
        else:
            print(order['error'])
        '''


    for coin in BUY_FAT_FINGERS:
        ticker_info = api.
        currentPrice = 0 # API TODO
        currentBid = 1
        currentAsk = 2
        COIN_PRICE.append(currentPrice)

    minOrderAmount = getMinOrderAmount()

    while True:
        print("Updating orders")

        for i, coin in enumerate(COIN_LIST):
            currentPrice = coin[0]

            # Check if any sells were hit first
            coinBalance = getCoinBalance(coin) #getRecentTrades()?
            # Don't collect free coins, if you own coins then it's assumed that you caught a fat finger
            if coinBalance > 0 and getRecentOrders(coin, 5):
                dumpCoin(coin)
            # Make sure the buffer is maintained within 25% of the buffer size, this is sort of abitrary but I think it'll work
            if COIN_PRICE[i]:
                bufferedPrice = (COIN_PRICE[i] - COIN_PRICE[i] * (PRICE_BUFFER * .25))
                print(currentPrice)
                print(bufferedPrice)
                if currentPrice < bufferedPrice:
                    cancelOrders(coin)
                    setOrders(coin)

                COIN_PRICE[i] = currentPrice

        time.sleep(60)

#Data gathering functions, for research purposes and not needed for the program to work
def getFatFingers():
    """
    Gets all fat fingers for a coin, average FF drop, and frequency of FFs
    """
    data = gmd
    # returns timestamps
    pass


def email_me(order_type, coin_ticker, coins_transacted, order_price):
    """
    email_me('Bought', 'MANA', 157, round(.000024, 6))
    """
    # me == the sender's email address
    # you == the recipient's email address

    bot_address = 'rawmeta3000@gmail.com'
    recipient_email = 'rawmeat3000@gmail.com'
    subject = 'Fat Finger ' + order_type
    message = '{} {} {} at {} for {}'.format(order_type, coins_transacted, coin_ticker, order_price, coins_transacted * order_price)

    formatted_email = email.message.Message()
    formatted_email.add_header('From', 'Fat Finger Bot <{}>'.format( bot_address ))
    formatted_email.add_header('To', recipient_email)
    formatted_email.add_header('Subject', subject)
    formatted_email.set_payload(message)

    mail = smtplib.SMTP('smtp.gmail.com', 587)
    mail.ehlo()
    mail.starttls()
    mail.login(bot_address, '19733@g12Alem75.142;')
    mail.sendmail(bot_address, 'rawmeat3000@gmail.com', formatted_email.as_string())
    mail.close()
    print("Sent")


def _requests(method, url):
    """
    someday I'll use this to replace the 'requests' module with urllib
    So this program can be easier to share, using only built in modules
    """
    with urllib.request.urlopen(url) as response:
        return response.read() # Returns http.client.HTTPResponse.


# Do the thing
main()