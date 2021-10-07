"""
This module is gathering all the data needed from Binance and Twitter Trend API to compile a message ready to use on Discord.
"""

import json
import pandas as pd
import datetime as dt
import requests
pd.options.mode.chained_assignment = None #needed to avoid warning in the log file

def twitter_status() -> list:
    """
    This function is using twittertrendAPI to retrieve data with a given hashtag.

    :return info : information from the given hashtag
    """
    BASE = "https://twittetrandapi.herokuapp.com/"
    response = requests.get(BASE + "Bitcoin")
    d = json.loads(response.text)
    score = float(d["final_score"])
    tweet = str(d["best_tweet"])
    account = str(d["best_account"])
    if score <= -0.01:
        info_score = "négatif :cloud: "
    elif score <= 0.12:
        info_score = "neutre :white_sun_cloud:"
    else:
        info_score = "positif :sunny:"
    info = ["**__Analyse Twitter :bird: :__**",
            "Meilleur compte twitter :arrow_right: " + account,
            "Meilleur tweet :arrow_right: " + tweet,
            "Sentiment global (30 derniers tweets):arrow_right: " + info_score,
            "   ",
            "**__Analyse des cours crypto : __**",]

    return info

def get_data(symbol:str, interval : str, dict_symbol : dict) -> (list, bool):
    """
    This function is getting all the data from Binance and it compute everything with the moving average algorithm.

    :param symbol : This is the symbol of the crypto currency.
    :param interval : This is the interval of the analysis. It can be 1d for one day or 1h for one hour.
    :param dict_symbol : This is the dictionnary of the allowed symbol.

    :return df : The function returns a data frame with all the information needed.
    :return success : It also return if the function did work or not.
    """
    try:
        symbol = dict_symbol[symbol]
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
    MMC = df['close'].ewm(span=min_average).mean().to_numpy() #Exponential Moving average short terme
    MML = df['close'].ewm(span=max_average).mean().to_numpy() #Exponential Moving average long terme
    MM_Volume = df['volume'].ewm(span=min_average).mean().to_numpy()  #Moving average volume
    Spread = MMC - MML

    df["MMC"] = MMC
    df["MML"] = MML
    df["MM_Volume"] = MM_Volume
    df["Spread"] = Spread
    df["Status"] = pd.Series(dtype='str')

    ## Intersection detection
    STATUS = []
    for i in range(0, len(MMC)):
        if MMC[i] >= MML[i]:
            STATUS.append("above")
            if MML[i] > MML[i-1] and df["Spread"][i] > df["Spread"][i-1]:
                state = "Tendance à la hausse, vous pouvez acheter! (Attention c'est peut être trop TARD) :white_sun_cloud: "
            else:
                state = "Attendez pour vendre... :cloud: "

        elif MMC[i] < MML[i]:
            STATUS.append("below")
            if MML[i] > MML[i - 1] and df["Spread"][i] < df["Spread"][i-1]:
                state = "Tendance à la hausse, vous pouvez acheter! (Attention c'est peut être trop TOT) :white_sun_cloud: "
            else:
                state = "Attendez pour acheter... :cloud: "

        if i > 0:
            if STATUS[i] != STATUS[i-1]:
                if STATUS[i] == "above":
                    if df['MM_Volume'][i] >= 40 and MML[i] > MML[i - 1]:
                        state = "Achetez aujourd'hui!! :sunny: "
                    elif MML[i] > MML[i - 1]:
                        state = "Vous pouvez achetez mais les volumes de sont pas élevés :sunny: "
                    else:
                        state = "Attendez :cloud: "

                elif STATUS[i] == "below":
                    state = "Vendez aujourd'hui!! :zap: "

        df['Status'][i] = state
    success = True
    return df, success

def get_status(interval :str, tweet :bool) -> str:
    """
    This function is compiling the data retrieved from the from the function get_data and from the twitter trend api.

    :param interval : This is the interval of the analysis. It can be 1d for one day or 1h for one hour.
    :param tweet: This is defining if the tweet analysis has to be done or not.
    :return MESSAGE : The message ready to be deployed on discord.
    """
    if tweet:
        MESSAGE = twitter_status()
    else :
        MESSAGE = [""]

    dict_symbol = {"ADA": "ADAUSDT",
            "AVALANCHE": "AVAXUSDT",
            "BITCOIN": 'BTCUSDT',
            "BNB": "BNBUSDT",
            "CAKECOIN": 'CAKEUSDT',
            "DOGECOIN": 'DOGEUSDT',
            "ETH": 'ETHUSDT',
            "LITECOIN": 'LTCUSDT',
            "SHIBA": "SHIBUSDT",
            "VET": "VETUSDT",
            "XRP": "XRPUSDT"
            }

    for i in range(0, len(dict_symbol.items())):
        symbol = list(dict_symbol.keys())[i]
        df, success = get_data(symbol, interval, dict_symbol)

        if success:
            price = float((df['close'][-1]))
            if symbol == "SHIBA":
                price = '{:,.6f}'.format(price).replace(',', ' ')
            else:
                price = '{:,.3f}'.format(price).replace(',', ' ')
            msg = list(dict_symbol.keys())[i] + " = " + str(price) + "$ :arrow_right: " + df['Status'][-1]

        else:
            msg = "Symbol " + list(dict_symbol.keys())[i] + " do not exist."

        MESSAGE.append(msg)

    return MESSAGE
