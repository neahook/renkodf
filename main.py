import pandas as pd
import yfinance as yf
from datetime import datetime
import pandas_ta as ta


atrsize = 0.25

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


# Define a start date and End Date
start = '2021-10-01'#setting today date as End Date
end = datetime.today().strftime('%Y-%m-%d')
df_ticks = yf.download(tickers="GBPUSD=X", start= start , end = end , interval ="1d")



bricks = ta.sma((ATR(df_ticks,14))["ATR"],50).iloc[-1]*atrsize


print(f"Brick Size: {bricks}")

# Define a start date and End Date
start = '2023-10-01'#setting today date as End Date
end = datetime.today().strftime('%Y-%m-%d')
df_ticks = yf.download(tickers="GBPUSD=X", start= start , end = end , interval ="1h")

df_ticks.rename(columns={'Close': 'close'}, inplace=True)
df_ticks.head(3)
df_ticks.tail(3)



from renkodf import Renko
r = Renko(df_ticks, brick_size=bricks)
df = r.renko_df('normal') # 'wicks' = default 
df.head(3)
df.tail(3)



import mplfinance as mpf
mpf.plot(df, type='candle', volume=True, style="charles", 
         title=f"renko: normal\nbrick size: {bricks}")
mpf.show()
# same as:
# r.plot('normal')



#df_wicks = r.renko_df('wicks')
#df_nongap = r.renko_df('nongap')
#
#fig = mpf.figure(style='charles', figsize=(12.5,9))
#fig.subplots_adjust(hspace=0.1, wspace=0.01)
#ax1 = fig.add_subplot(2,2,1)
#ax2 = fig.add_subplot(2,2,2)
#
#mpf.plot(df_wicks,type='candle',ax=ax1,axtitle='wicks', )
#mpf.plot(df_nongap,type='candle',ax=ax2,axtitle='nongap')
#mpf.show()