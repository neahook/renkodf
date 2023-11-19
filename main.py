import pandas as pd
import yfinance as yf
from datetime import datetime
import pandas_ta as ta
import pika
import logging
import json
import ssl
import time


atrsize = 0.25
#ticker = 'AUDUSD=X' #GBPUSD=X CL=F
#symbol = 'AUDUSD'
timeperiod = 60

# Define a start date and End Date
dstart = '2021-10-01'#setting today date as End Date
dend = datetime.today().strftime('%Y-%m-%d')

def ATR(DF, n):
    df = DF.copy() # making copy of the original dataframe
    df['H-L'] = abs(df['High'] - df['Low']) 
    df['H-PC'] = abs(df['High'] - df['Close'].shift(1))# high -previous close
    df['L-PC'] = abs(df['Low'] - df['Close'].shift(1)) #low - previous close
    df['TR'] = df[['H-L','H-PC','L-PC']].max(axis =1, skipna = False) # True range
    df['ATR'] = df['TR'].rolling(n).mean() # average –true range
    df = df.drop(['H-L','H-PC','L-PC'], axis =1) # dropping the unneccesary columns
    df.dropna(inplace = True) # droping null items
    return df




def getdata(ticker, symbol, precision):
    global atrsize, timeperiod, start, end
    
    print(ticker, symbol)
    df_ticks = yf.download(tickers=ticker, start= dstart , end =dend , interval ="1d")

    print(df_ticks)

    bricks = ta.sma((ATR(df_ticks,14))["ATR"],50).iloc[-1]*atrsize


    print(f"Brick Size: {bricks}")

    # Define a start date and End Date
    start = '2023-10-01'#setting today date as End Date
    end = datetime.today().strftime('%Y-%m-%d')
    df_ticks = yf.download(tickers=ticker, start= start , end = end , interval ="1h")

    df_ticks.rename(columns={'Close': 'close'}, inplace=True)
    df_ticks.head(3)
    df_ticks.tail(3)

    from renkodf import Renko
    r = Renko(df_ticks, brick_size=bricks)
    df = r.renko_df('normal') # 'wicks' = default 
    df.head(3)
    df.tail(3)

    df_wicks = r.renko_df('wicks')

    #print(df_wicks)

    if df_wicks["close"].iloc[-1] > df_wicks["close"].iloc[-2]:
        signal = 1
    elif df_wicks["close"].iloc[-1] < df_wicks["close"].iloc[-2]:
        signal = 2
    else:
        signal = 0

    #precision = len(str(df_wicks["close"].iloc[-1]).split(".")[1])

    if signal == 1:
        message = {
            "pair":f"{symbol}",
            "timeperiod":f"{timeperiod}",
            "open":f"{df_wicks['open'].iloc[-1]}",
            "high":f"{df_wicks['high'].iloc[-1]}",
            "low":f"{df_wicks['low'].iloc[-1]}",
            "close":f"{df_wicks['close'].iloc[-1]}",
            "SL":f"{df_wicks['open'].iloc[-1]-(4*bricks)}",
            "TP":f"{df_wicks['open'].iloc[-1]+(12*bricks)}",
            "brick":f"{bricks}",
            "precision":f"{precision}",
            "signal":f"{signal}",
            "source":"PythonRenko001"
        }
    if signal == 2:
        message = {
            "pair":f"{symbol}",
            "timeperiod":f"{timeperiod}",
            "open":f"{df_wicks['open'].iloc[-1]}",
            "high":f"{df_wicks['high'].iloc[-1]}",
            "low":f"{df_wicks['low'].iloc[-1]}",
            "close":f"{df_wicks['close'].iloc[-1]}",
            "SL":f"{df_wicks['open'].iloc[-1]+(4*bricks)}",
            "TP":f"{df_wicks['open'].iloc[-1]-(12*bricks)}",
            "brick":f"{bricks}",
            "precision":f"{precision}",
            "signal":f"{signal}",
            "source":"PythonRenko001"
        }



    parameters = pika.URLParameters('amqp://oecjousy:a9tnF_i_Oaz3H2LNze1ljxSNOD0rsCip@kangaroo.rmq.cloudamqp.com/oecjousy')
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    channel.queue_declare(queue='signals', durable=True) 
    message = json.dumps(message)
    #message = message.encode('utf8') 
    channel.basic_publish(
        exchange='',
        routing_key='signals', 
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE,
            priority=0, # default priority
            expiration= "3600000"
        ))
    
    connection.close()
    logging.info(f"Signal Msg Transmitted {ticker}: {message}")

    #time.sleep(5)




pairs = [('AUDUSD=X', 'AUDUSD', 5),
         ('EURUSD=X', 'EURUSD', 5),
         ('GBPUSD=X', 'GBPUSD', 5),
         ('NZDUSD=X', 'NZDUSD', 5),
         ('USDCAD=X', 'USDCAD', 5),
         ('USDCHF=X', 'USDCHF', 5),
         ('CL=F', 'USOUSD', 3),
         ('USDJPY=X', 'USDJPY', 3)]

for pair in pairs:
    getdata(pair[0], pair[1], pair[2])