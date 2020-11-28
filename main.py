from binance.client import Client
import os
import numpy as np
import pandas as pd
from datetime import datetime
import time
import talib._ta_lib as ta
from binance.websockets import BinanceSocketManager
from binance.exceptions import BinanceAPIException, BinanceOrderException
from twisted.internet import reactor

crypt_symbol = 'BTCUSDT'
binance_api = open('C:\\Account IDs\\binance_api.txt', 'r').read()
binance_secret = open('C:\\Account IDs\\binance_secret.txt', 'r').read()
client = Client(binance_api, binance_secret)
#btc_price = client.get_symbol_ticker(symbol='BTCUSDT')
#print(btc_price)
# timestamp = client._get_earliest_valid_timestamp('BTCUSDT', '1m')
# print(timestamp)
new_bars = {'open':None,'high':None,'low':None,'close':None}
btc_price = {'error':False}
openPrice = {'BTCUSDT': None, 'error':False}
highPrice = {'BTCUSDT': None, 'error':False}
lowPrice = {'BTCUSDT': None, 'error':False}
closePrice = {'BTCUSDT': None, 'error':False}



def btc_trade_history(msg):
    ''' define how to process incoming WebSocket messages '''
    if msg['e'] != 'error':
        openPrice['BTCUSDT'] = msg['k']['o']
        highPrice['BTCUSDT'] = msg['k']['h']
        lowPrice['BTCUSDT'] = msg['k']['l']
        closePrice['BTCUSDT'] = msg['k']['c']
        #print(msg['k']['i'])
        #new_bars = {'open':msg['k']['o'],'high':msg['k']['h'],'low':msg['k']['l'],'close':msg['k']['c']}
        #dataframe = dataframe.append(new_bars, ignore_index=True)
        #print(new_bars)
    else:
        btc_price['error'] = True

def get_data():
    btc_df = pd.DataFrame(columns=['open', 'high', 'low', 'close'])
    t = 'T'
    timeZone = '-05:00'
    ct = datetime.now().strftime(f'%m/%d/%Y{t}%H:%M{timeZone}')
    # request historical candle (or klines) data
    bars = client.get_historical_klines(symbol=crypt_symbol, interval='1m', start_str=ct)
    #print(bars)
    # new_bars = {'date':bars[0][0],'open':bars[0][1],'high':bars[0][2],'low':bars[0][3],'close':bars[0][4]}
    for i in bars:
        new_bars = {'open':i[1],'high':i[2],'low':i[3],'close':i[4]}
        btc_df = btc_df.append(new_bars, ignore_index=True)
    #btc_df.set_index('date', inplace=True)
    btc_df = calc_ema(btc_df)
    return btc_df

def calc_ema(dataframe):
    dataframe['ema5'] = ta.EMA(dataframe['close'],timeperiod=5)
    dataframe['ema10'] = ta.EMA(dataframe['close'],timeperiod=10)
    return dataframe

def buy_sell_calc(self, dataframe):
    # make sure we get the actual symbol
    # check if we can sell
    #TODO can probably add check if ticker_symbol postion is None so that it doesn't have to calculate all of this
    if (dataframe['ema5'][dataframe.index[-1]] > dataframe['ema10'][dataframe.index[-1]]):
        if (dataframe['ema5'][dataframe.index[-2]] > dataframe['ema10'][dataframe.index[-2]]): # making sure the it is tending to move upwards
                if self.get_positions_sell(ticker_symbol) is not None:
                    qty, orderside = self.get_positions_sell(ticker_symbol)
                    if orderside == 'long':
                        #limit_price = round(dataframe['close'][dataframe.index[-1]],2) #TODO either take out limit for sell or make it from low column not close
                        self.submitOrder_sell(qty,ticker_symbol,'sell')
    # check if we can buy
    if (dataframe['ema5'][dataframe.index[-1]] < dataframe['ema10'][dataframe.index[-1]]):
        if (dataframe['ema5'][dataframe.index[-2]] < dataframe['ema10'][dataframe.index[-2]]):
                if can_buy == True:
                    quantity = self.calc_num_of_stocks(dataframe)
                    #limit = round(dataframe['close'][dataframe.index[-1]],2)
                    stop = str(round(dataframe['close'][dataframe.index[-1]]*.95,2))
                    stop_loss = {"stop_price": stop, "limit_price": stop}
                    self.submitOrder_buy(quantity,ticker_symbol,'buy',stop_loss)

def main():
    df = get_data()
    # ct = datetime.now().strftime("%S")
    # # init and start the WebSocket
    # bsm = BinanceSocketManager(client)
    # #conn_key = bsm.start_symbol_ticker_socket(crypt_symbol, btc_trade_history)
    # conn_key = bsm.start_kline_socket(crypt_symbol, btc_trade_history)
    # while ct != "59":
    #     ct = datetime.now().strftime("%S")
    #     if ct == "59":
    #         continue
    # while True:
    #     try:
    #         if ct == '58':
    #             bsm.start()
    #             # put script to sleep to allow WebSocket to run for a while
    #             # this is just for example purposes
    #             time.sleep(2)
    #             # stop websocket
    #             bsm.stop_socket(conn_key)
    #             # properly terminate WebSocket
    #             reactor.stop()
    #             y = {'open': data['open'],'close':data['close']}
    #             bitcoin_data = bitcoin_data.append(y, ignore_index=True)
    #             calc_ema(bitcoin_data)
    #             if len(bitcoin_data) > 70:
    #                 bitcoin_data = bitcoin_data.drop(bitcoin_data.index[0])
    #             print(bitcoin_data)
    #         ct = datetime.now().strftime("%S")
    #         time.sleep(.5)
    #     except Exception as e:
    #         print(f'Error: {str(e)}')

if __name__ == '__main__':
    #main()
    df = get_data()
    time.sleep(58)
    # init and start the WebSocket
    print(df)
    bsm = BinanceSocketManager(client)
    #conn_key = bsm.start_symbol_ticker_socket(crypt_symbol, btc_trade_history)
    conn_key = bsm.start_kline_socket(crypt_symbol, btc_trade_history)
    bsm.start()
    while not closePrice['BTCUSDT']:
	# wait for WebSocket to start streaming data
	    time.sleep(0.1)

    while True:
        # error check to make sure WebSocket is working
        if openPrice['error']:
            # stop and restart socket
            bsm.stop_socket(conn_key)
            bsm.start()
            openPrice['error'] = False
            lowPrice['error'] = False
            highPrice['error'] = False
            closePrice['error'] = False
        else:
		    #if price['BTCUSDT'] > 10000:
            try:
                y = {'open':openPrice['BTCUSDT'],'high':highPrice['BTCUSDT'],'low':lowPrice['BTCUSDT'],'close':closePrice['BTCUSDT']}
                df = df.append(y, ignore_index = True)
                df = calc_ema(df)
                print(df)
                break
            except BinanceAPIException as e:
                # error handling goes here
                print(e)
            except BinanceOrderException as e:
                # error handling goes here
                print(e)
        time.sleep(0.1)
    #bsm.start()
    #df = df.append(new_bars, ignore_index=True)
    #print(df)
    # put script to sleep to allow WebSocket to run for a while
    # this is just for example purposes
    #time.sleep(10)

    # stop websocket
    bsm.stop_socket(conn_key)

    # properly terminate WebSocket
    reactor.stop()