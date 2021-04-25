import requests
import json
import pandas as pd
import datetime as dt
pd.options.mode.chained_assignment = None #needed to avoid warning in the log file

def get_data(symbol, interval, dict):
    try:
        symbol = dict[symbol]
    except KeyError:
        success = False
        df = None
        return df, success

    url = "https://api.binance.com/api/v3/klines"
    endTime = dt.datetime.now()
    if interval == '1d':
        startTime = endTime - dt.timedelta(days=90)
    elif interval == '1h':
        startTime = endTime - dt.timedelta(hours=90)

    limit = 1000 #max limit
    min_average = 2 #short moving average
    max_average = 20 #long moving average

    #getting data from binance API
    req_params = {"symbol": symbol,
                  "interval": interval,
                  "endTime": str(int(endTime.timestamp()*1000)),
                  "startTime": str(int(startTime.timestamp()*1000)),
                  "limit": limit}
    df = pd.DataFrame(json.loads(requests.get(url, req_params).text))

    df = df.iloc[:, 0:6]
    df.columns = ['datetime', 'open', 'high', 'low', 'close', 'volume']
    df.open = df.open.astype("float")
    df.high = df.high.astype("float")
    df.low = df.low.astype("float")
    df.close = df.close.astype("float")
    df.volume = df.volume.astype("float")
    df.index = [dt.datetime.fromtimestamp(x / 1000.0) for x in df.datetime]
    df['volume'] = df['volume'].astype("float") / max(df['volume'].astype("float")) * 100

    #Moving Average calculation
    MMC = df['close'].rolling(min_average).mean().to_numpy() #Moving average court terme
    MML = df['close'].rolling(max_average).mean().to_numpy() #Moving average long terme
    MM_Volume = df['volume'].rolling(min_average).mean().to_numpy()  #Moving average volume
    Spread = MMC - MML

    df["MMC"] = MMC
    df["MML"] = MML
    df["MM_Volume"] = MM_Volume
    df["Spread"] = Spread
    df["Status"] = pd.Series(dtype='str')

    ## Intersection detection
    STATUS = []
    for i in range(max_average, len(MMC)):
        if MMC[i] > MML[i]:
            STATUS.append("above")
            if MML[i] > MML[i-1] and df["Spread"][i] > df["Spread"][i-1]:
                state = "In a up-trend. You can buy ! (it might be too late) "
            else:
                state = "Wait for sell..."

        if MMC[i] < MML[i]:
            STATUS.append("below")
            if MML[i] > MML[i - 1] and df["Spread"][i] < df["Spread"][i-1]:
                state = "In a up-trend. You can buy ! (it might be early)"
            else:
                state = "Wait for buy..."

        if i > max_average + min_average:
            if STATUS[i-max_average] != STATUS[i-(max_average+1)]:
                if STATUS[i-max_average] == "above":
                    if df['MM_Volume'][i] >= 50 and MML[i] > MML[i - 1]:
                        state = "Buy Today!!"
                    elif MML[i] > MML[i - 1]:
                        state = "You can buy but it's not a volume trend"
                    else:
                        state = "Wait"

                elif STATUS[i-max_average] == "below":
                    state = "Sell Today!!"

        df['Status'][i] = state
    success = True
    return df, success

#Message creation from data retrieved
def get_status(interval):
    MESSAGE = []
    dict = {"BITCOIN": 'BTCUSDT',
            "ETH": 'ETHUSDT',
            "XRP": "XRPUSDT",
            "LITECOIN": 'LTCUSDT',
            "DOGECOIN": 'DOGEUSDT',
            "CAKECOIN": 'CAKEUSDT',
            "BNB": "BNBUSDT"}

    for i in range(0, len(dict.items())):
        symbol = list(dict.keys())[i]
        df, success = get_data(symbol, interval, dict)

        if success:
            msg = list(dict.keys())[i] + " : " + df['Status'][-1]
        else:
            msg = "Symbol " + list(dict.keys())[i] + " do not exist."

        MESSAGE.append(msg)

    return MESSAGE