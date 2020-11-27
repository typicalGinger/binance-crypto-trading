import ccxt
import os
import numpy as np
import pandas as pd
from datetime import datetime
import time
import talib._ta_lib as ta

crypt_symbol = 'BTC/USD'
binance_api = open('C:\\Account IDs\\binance_api.txt', 'r').read()
binance_secret = open('C:\\Account IDs\\binance_secret.txt', 'r').read()
webullpassword = open('C:\\Account IDs\\email.txt', 'r').read()
email = open('C:\\Account IDs\\webullpassword.txt', 'r').read()
binance = ccxt.binanceus({'apiKey': binance_api,'secret': binance_secret})
binance.load_markets()

def get_certain_data():
    bitcoin_df = pd.DataFrame(columns=['open','close'])
    ct = datetime.now().strftime("%S")
    while ct != "59":
        ct = datetime.now().strftime("%S")
        if ct == "59":
            continue
    data = binance.fetch_ticker(symbol=crypt_symbol)
    y = {'open': data['open'],'close':data['close']}
    #print(type(data))
    bitcoin_df = bitcoin_df.append(y, ignore_index=True)
    #print(bitcoin_df)
    #print('ok')
    c = 0
    while len(bitcoin_df) < 22:
        time.sleep(59.8)
        data = binance.fetch_ticker(symbol=crypt_symbol)
        y = {'open': data['open'],'close':data['close']}
        bitcoin_df = bitcoin_df.append(y, ignore_index=True)
        c += 1
        print(c)
    calc_ema(bitcoin_df)
    print(bitcoin_df)
    return bitcoin_df

def calc_ema(dataframe):
    dataframe['ema5'] = ta.EMA(dataframe['close'],timeperiod=5)
    dataframe['ema10'] = ta.EMA(dataframe['close'],timeperiod=10)
    dataframe['ema20'] = ta.EMA(dataframe['close'],timeperiod=20)
    return dataframe

def buy_sell_calc(self, dataframe, ticker):
    # make sure we get the actual symbol
    ticker_symbol = ticker['symbol']
    # check if we can sell
    #TODO can probably add check if ticker_symbol postion is None so that it doesn't have to calculate all of this
    if (dataframe['ema5'][dataframe.index[-1]] > dataframe['ema10'][dataframe.index[-1]] and dataframe['ema5'][dataframe.index[-1]] > dataframe['ema20'][dataframe.index[-1]] and dataframe['ema10'][dataframe.index[-1]] > dataframe['ema20'][dataframe.index[-1]]):
        if (dataframe['ema5'][dataframe.index[-2]] > dataframe['ema10'][dataframe.index[-2]] and dataframe['ema5'][dataframe.index[-2]] > dataframe['ema20'][dataframe.index[-2]] and dataframe['ema10'][dataframe.index[-2]] > dataframe['ema20'][dataframe.index[-2]]): # making sure the it is tending to move upwards
            if (((dataframe['ema5'][dataframe.index[-1]]-dataframe['ema10'][dataframe.index[-1]])/dataframe['ema10'][dataframe.index[-1]]*100) > .5 and ((dataframe['ema5'][dataframe.index[-1]]-dataframe['ema20'][dataframe.index[-1]])/dataframe['ema20'][dataframe.index[-1]]*100) > 2):
                if self.get_positions_sell(ticker_symbol) is not None:
                    qty, orderside = self.get_positions_sell(ticker_symbol)
                    if orderside == 'long':
                        #limit_price = round(dataframe['close'][dataframe.index[-1]],2) #TODO either take out limit for sell or make it from low column not close
                        self.submitOrder_sell(qty,ticker_symbol,'sell')
    # check if we can buy
    if (dataframe['ema5'][dataframe.index[-1]] < dataframe['ema10'][dataframe.index[-1]] and dataframe['ema5'][dataframe.index[-1]] < dataframe['ema20'][dataframe.index[-1]] and dataframe['ema10'][dataframe.index[-1]] < dataframe['ema20'][dataframe.index[-1]]):
        if (dataframe['ema5'][dataframe.index[-2]] < dataframe['ema10'][dataframe.index[-2]] and dataframe['ema5'][dataframe.index[-2]] < dataframe['ema20'][dataframe.index[-2]] and dataframe['ema10'][dataframe.index[-2]] < dataframe['ema20'][dataframe.index[-2]]):
            if (dataframe['ema5'][dataframe.index[-3]] < dataframe['ema10'][dataframe.index[-3]] and dataframe['ema5'][dataframe.index[-3]] < dataframe['ema20'][dataframe.index[-3]] and dataframe['ema10'][dataframe.index[-3]] < dataframe['ema20'][dataframe.index[-3]]):
                can_buy = self.get_positions_buy(ticker_symbol)
                if can_buy == True:
                    quantity = self.calc_num_of_stocks(dataframe)
                    #limit = round(dataframe['close'][dataframe.index[-1]],2)
                    stop = str(round(dataframe['close'][dataframe.index[-1]]*.95,2))
                    stop_loss = {"stop_price": stop, "limit_price": stop}
                    self.submitOrder_buy(quantity,ticker_symbol,'buy',stop_loss)

def main():
    hist = get_data()
    ct = datetime.now().strftime("%S")
    while ct != "58":
        ct = datetime.now().strftime("%S")
        if ct == "58":
            continue
    while True:
        try:
            new_hist = pd.DataFrame(new_hist)
            hist = hist.append(new_hist, ignore_index=True)
            calc_ema(hist)
            if len(hist) > 25:
                hist = hist.drop(hist.index[0])
            print(hist)
            time.sleep(60)
        except Exception as e:
            print(f'Error: {str(e)}')

if __name__ == '__main__':
    main()