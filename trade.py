# SCript for binary options trading test

import time
#import requests
from random import random
from api import get_spot

class Trade:

    def __init__(self, duration, trading_amt, total_bal, trade_type):
        # get the current price of asset with GET request
        # check the price change every 5 secs and update user
        # at the end of 60sec compair the current price to the movement predicted
        self.duration = duration
        self.trading_amt = trading_amt
        self.total_bal = total_bal
        self.trade_type = trade_type

        # if trade_type == 'CALL':
        #     bet_quote = self.get_price('BTC-USD')
        #     print("The bet_quote is: " + str(round(bet_quote, 4)) + " Trade type: "+ self.trade_type)
        #     result = None

        #     for i in range(0, self.duration, 5):
        #         current_quote = self.get_price('BTC-USD')
        #         if(i >= self.duration):
        #             break
        #         result = self.call(bet_quote, current_quote)
        #         time.sleep(5)
        #         i+=5
        # else:
        #     bet_quote = self.get_price('BTC-USD')
        #     print("The bet_quote is: " + str(round(bet_quote, 4)) +" Trade Type: "+ self.trade_type)
        #     result = None

        #     for i in range(0, self.duration, 5):
        #         current_quote = self.get_price('BTC-USD')
        #         if(i >= self.duration):
        #             break
        #         result = self.put(bet_quote, current_quote)
        #         time.sleep(5)
        #         i+=5

    
    # get price quote method
    def get_price(self, pair):
        self.pair = pair
        spot_quote = get_spot(self.pair)
        
        # print("The xrp price", rand_quote)
        return float(spot_quote)

    # the call trade type function
    def call(self, bet_quote, current_quote, perc_profit):
        self.bet_quote = bet_quote
        self.current_quote = current_quote
        state = None
        new_balance = None

        if(self.current_quote > self.bet_quote):
            new_balance = ((self.trading_amt*perc_profit)/100) + self.total_bal
            state = "TRADE AMOUNT: <b>"+str(self.trading_amt)+"</b>\nP/L:  <b>+"+ str(((self.trading_amt*perc_profit)/100)) + " ("+str(perc_profit)+")</b>\n\nNGN BALANCE: " + str(new_balance)
        else:
            new_balance = (self.total_bal - self.trading_amt)
            state = "TRADE AMOUNT: <b>"+str(self.trading_amt)+"</b>\nP/L:  <b>-"+ str(self.trading_amt) + "</b>\n\nNGN BALANCE: " + str(new_balance)

        return { "state": state, "new_balance": new_balance }

    # the put trade type function
    def put(self, bet_quote, current_quote, perc_profit):
        self.bet_quote = bet_quote
        self.current_quote = current_quote
        state = None
        new_balance = None

        if(self.current_quote < self.bet_quote):
            new_balance = ((self.trading_amt*perc_profit)/100) + self.total_bal
            state = "TRADE AMOUNT: <b>"+str(self.trading_amt)+"</b>\nP/L: <b>+"+ str(((self.trading_amt*perc_profit)/100)) + " ("+str(perc_profit)+")</b>\n\nNGN BALANCE: " + str(new_balance)
        else:
            new_balance = (self.total_bal - self.trading_amt)
            state = "TRADE AMOUNT: <b>"+str(self.trading_amt)+"</b>\nP/L: <b>-"+ str(self.trading_amt) + "</b>\n\nNGN BALANCE: " + str(new_balance)

        return { "state": state, "new_balance": new_balance }


# def main():
#     trade = Trade(60, 10, 1000, 'CALL')
#     print("The trade is done")

# if __name__ == '__main__':
#     main()
