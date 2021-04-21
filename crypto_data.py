import requests
import json
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
pd.options.mode.chained_assignment = None


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
        startTime = endTime - dt.timedelta(90)
    elif interval == '1h':
        startTime = endTime - dt.timedelta(hours=90)

    limit = 1000
    min_average = 2
    max_average = 20

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

    ## Moving Average
    MMC = df['close'].rolling(min_average).mean().to_numpy() #Moving average court terme
    MML = df['close'].rolling(max_average).mean().to_numpy() #moving average long terme
    MM_Volume = df['volume'].rolling(15).mean().to_numpy()  # moving average volume

    df["MMC"] = MMC
    df["MML"] = MML
    df["MM_Volume"] = MM_Volume

    df["Status"] = pd.Series(dtype='str')
    ## Intersection detection
    STATUS = []

    for i in range(max_average, len(MMC)):
        if MMC[i] > MML[i]:
            STATUS.append("above")
            if MML[i] > MML[i-1]:
                state = "In a up-trend. You might wait for sell or you can buy."
            else:
                state = "Wait for sell or hold-on..."

        if MMC[i] < MML[i]:
            if MML[i] > MML[i - 1]:
                state = "In a up-trend. You might wait for buy or you can buy now."
            else:
                state = "Wait for buy or hold on..."
            STATUS.append("below")

        if i > max_average + 2:
            if STATUS[i-max_average] != STATUS[i-(max_average+1)]:
                if STATUS[i-max_average] == "above":
                    if df['MM_Volume'][i] >= 50:
                        state= "Buy Today!!"
                    else:
                        state = "You might buy but it's not a volume-trend."

                elif STATUS[i-max_average] == "below":
                    state = "Sell Today!!"

        df['Status'][i] = state
    success = True
    return df, success

def get_status(interval):
    MESSAGE = []
    dict = {"BITCOIN": 'BTCUSDT',
            "ETH": 'ETHUSDT',
            "XRP": "XRPUSDT",
            "LITECOIN": 'LTCUSDT',
            "DOGECOIN": 'DOGEUSDT'}

    for i in range(0, len(dict.items())):
        symbol = list(dict.keys())[i]
        df, success = get_data(symbol, interval, dict)

        #df['close'].astype("float").plot()
        #df['MMC'].astype("float").plot()
        #df['MML'].astype("float").plot()
        #plt.title(list(dict.keys())[i])
        #plt.show()

        if success:
            msg = list(dict.keys())[i] + " : " + df['Status'][-1]
        else:
            msg = "Symbol " + list(dict.keys())[i] + " do not exist."

        MESSAGE.append(msg)

    return MESSAGE

#MESSAGE = get_status("1h")
#info = "\n".join(MESSAGE)
#print(info)
