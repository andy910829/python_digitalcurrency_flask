import json,requests,urllib3 
import pandas as pd  
import numpy as np  
import talib
urllib3.disable_warnings()

class getprice:  
    def __init__(self):
        pass
    def check(security,  count, frequency):
        url = f'https://api.binance.com/api/v3/klines?interval={frequency}&limit={count}&symbol={security}'
        res = requests.get(url)
        if res.status_code == 400:
            return False
        else:
            return True
            
    def get_closeprice(security,  count, frequency):  
        try:
            url = f'https://api.binance.com/api/v3/klines?interval={frequency}&limit={count}&symbol={security}'
            res = requests.get(url, verify=False).text
            df = pd.DataFrame(json.loads(res))
            df.columns = ['time', 'open', 'high', 'low', 'close', 'vol', 'close_time', 'turnover', 'turn', 'buy_vol',
                        'buy_amount', 'a']
            #df["time"] = pd.to_datetime(df["time"]+8*3600*1000, unit='ms')
            df = df[['time', 'open', 'close', 'high', 'low', 'vol']]  
            #df.set_index(["time"], inplace=True)
            df = df.astype("float")
            #df = df.reset_index()
            return df["close"] 
        except:
            return 
    def get_highprice(security,  count, frequency):  
        try:
            url = f'https://api.binance.com/api/v3/klines?interval={frequency}&limit={count}&symbol={security}'
            res = requests.get(url, verify=False).text
            df = pd.DataFrame(json.loads(res))
            df.columns = ['time', 'open', 'high', 'low', 'close', 'vol', 'close_time', 'turnover', 'turn', 'buy_vol',
                        'buy_amount', 'a']
            df = df[['time', 'open', 'close', 'high', 'low', 'vol']]  
            df = df.astype("float")
            return df["high"]
        except:
            print("link error..")
            pass

    def get_lowprice(security,  count, frequency):  
        try:
            url = f'https://api.binance.com/api/v3/klines?interval={frequency}&limit={count}&symbol={security}'
            res = requests.get(url, verify=False).text
            df = pd.DataFrame(json.loads(res))
            df.columns = ['time', 'open', 'high', 'low', 'close', 'vol', 'close_time', 'turnover', 'turn', 'buy_vol',
                        'buy_amount', 'a']
            df = df[['time', 'open', 'close', 'high', 'low', 'vol']]  
            df = df.astype("float")
            return df["low"]
        except:
            print("link error..")
            pass

class strategy:
    def RSI_MA_SMA(madf, rsidf,  macddf,  rsi55df, currentprice, high, low):
        currentprice = currentprice.iloc[0]
        rsi55 = talib.RSI(rsi55df, timeperiod = 21)
        rsi21 = talib.RSI(rsidf, timeperiod = 21).filter(regex="21", axis=0).iloc[0]
        rsisma = talib.SMA(rsi55, 55).filter(regex="75", axis=0).iloc[0]
        ma = talib.MA(madf, 13).filter(regex="13", axis=0).iloc[0]
        fastperiod, slowperiod, signalperiod = talib.MACD(macddf, fastperiod = 13, slowperiod = 26, signalperiod = 9 )
        fastperiod, slowperiod, signalperiod = fastperiod.filter(regex="33", axis=0).iloc[0], slowperiod.filter(regex="33", axis=0).iloc[0], signalperiod.filter(regex="33", axis=0).iloc[0]
        recenthigh = max(high)
        recentlow = min(low)
        longstopwin = currentprice + (currentprice - recentlow)
        shortstopwin = currentprice - (recenthigh - currentprice)
        if fastperiod > slowperiod and  rsi21 > rsisma  and currentprice > ma:
            return "多", currentprice, longstopwin, recentlow
        elif fastperiod < slowperiod and rsi21 < rsisma and currentprice < ma:
            return "空", currentprice, shortstopwin, recenthigh
        else:
            return "None", "None", "None", "None"

    def vegas(ema144df , ema169df , ema576df , ema676df, currentprice, low):
        currentprice = currentprice.iloc[0]
        low = low.iloc[0]
        ema144 = talib.EMA(ema144df , timeperiod = 144).filter(regex="143", axis=0).iloc[0]
        ema169 = talib.EMA(ema169df , timeperiod = 169).filter(regex="168", axis=0).iloc[0]
        ema576 = talib.EMA(ema576df , timeperiod = 576).filter(regex="575", axis=0).iloc[0]
        ema676 = talib.EMA(ema676df , timeperiod = 676).filter(regex="675", axis=0).iloc[0]
        LONG_vegas = bool(ema144 > ema576 and ema144 > ema676 and ema169 > ema576 and ema169 > ema676)
        LONG_in = bool(low < ema144 and currentprice > ema169)
        short_vegas = bool(ema144 < ema576 and ema144 < ema676 and ema169 < ema576 and ema169 < ema676)
        short_in = bool(low >= ema144 and currentprice <= ema169)
        if (LONG_in and LONG_vegas) == True :
            STOPLOSS = ema676 #止損
            STOPWIN = currentprice+ (currentprice - ema676) #止贏
            return "多", currentprice, STOPWIN,STOPLOSS
        elif (short_vegas and short_in) == True :
            STOPLOSS = ema676 #止損
            STOPWIN = currentprice - (ema676 - currentprice) #止贏
            return "空", currentprice, STOPWIN, STOPLOSS
        else:
            return "None", "None", "None", "None"

# getprice.check("BTCUS", count = 1, frequency= "1m")
# statelist = []
# fre = "1m"
# while True:
#     state, currentprice, stopwin, stoploss = strategy.vegas(getprice.get_closeprice("BTCUSDT",  count = 144, frequency = fre),
#                                                             getprice.get_closeprice("BTCUSDT",  count = 169, frequency = fre),
#                                                             getprice.get_closeprice("BTCUSDT",  count = 576, frequency = fre),  
#                                                             getprice.get_closeprice("BTCUSDT",  count = 676, frequency = fre), 
#                                                             getprice.get_closeprice("BTCUSDT",  count = 1, frequency = fre),
#                                                             getprice.get_lowprice("BTCUSDT",  count = 10, frequency = fre))
#     statelist.append(state)
#     if len(statelist) == 5:
#         statelist.pop(0)
#         if statelist[3] != statelist[2] and statelist[3] != "None":
#             print(f"幣種:BTCUSDT\n進場價格:{currentprice}\n方向:{state}\n止盈:{stopwin}\n止損:{stoploss}")
#     print("123")


#   print(f"幣種:BTCUSDT\n進場價格:{currentprice}\n方向:{direction}\n止盈:\n止損:")


# def MACD(df):
#     fastperiod, slowperiod, signalperiod = talib.MACD(df, fastperiod = 13, slowperiod = 26, signalperiod = 9)    
#     print(fastperiod.filter(regex="33", axis=0).iloc[0], slowperiod.filter(regex="33", axis=0).iloc[0], signalperiod.filter(regex="33", axis=0).iloc[0])

# MACD(get_price("BTCUSDT",  count = 34, frequency = "1m"))



# df = get_price('BTCUSDT',count=5,frequency='1h')
# currentTime = datetime.now().strftime('%Y-%m-%d %H:00:00')
# currentdata = df[df["time"]==currentTime]
# # currentdata = df.loc["2022-07-06 20:00:00"]
# print((datetime.datetime.now()+ datetime.timedelta(hours=0)).strftime('%Y-%m-%d %H:00:00'))






            









        

