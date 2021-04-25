# Crypto Bot Documention  
## Principle
The algorithm is based on the moving average algorithm.
The first step of this algorithm is to create two curves :
* Short moving average curve (2 periods in this case)
* Long moving average curve (20 periods in this case)

The two moving average curves are based on the closing prices curve
on the given period (1 day or 1 hour).
When the short moving average curve is crossing 
the long moving average curve from __below__ then it is time to buy stocks.
When the short moving average curve is crossing 
the long moving average curve from __above__ then it is time to sell stocks.

In our case, we find out that the moving average combination 2/20 seems to
be optimized for cryptocurrency.

For example, here is a plotting of the closing prices for the Bitcoin. 
There is also the MMC curve (2 days moving average) and the MML (20 days moving average).

![Bitcoin](/pictures/Bitcoin.png)

It this plotting you can see that the moving average algorithm advised to 
sell on 2021-04-18 because the short moving average curve (MMC) is crossing 
the long moving average curve (MML) from __above__.
This algorithm has been a bit enhanced in this
application because trend volume, the derivative
of the long-term moving average and the spread 
between the short and long term moving average curves 
are also considered.

## Principle in application
In this application, there is 2 cases:
* daily alerts
* daily trend recommendation

#### Daily alerts
The daily alerts program is running our moving average algorithm 
every hour with a period of time of 1 hour.
If one cryptocurrency has to be sold or has to be bought then an
alerts is automatically sent to the correct discord channel.

#### Daily trend recommendation
The daily trend recommendation program is running our moving average 
algorithm with a period of time of 1 day every morning (8:30) and every evening (17:30).
Recommendation is sent for every tracked cryptocurrency in the right
Discord channel.

## Recommendation dictionary
#### Case 1
When the short term moving average (MMC) is __higher__ than
the long-term moving average (MML).

![Case 1](/pictures/Case1.png)

Situation | Recommendation
------------ | -------------
If the long-term moving average (MML) is increasing and if the spread is increasing. | In a up-trend. You can buy ! (it might be too late)
Else | Wait for sell..

#### Case 2
When the short term moving average (MMC) is __lower__ than
the long-term moving average (MML).

![Case 2](/pictures/Case2.png)

Situation | Recommendation
------------ | -------------
If the long-term moving average (MML) is increasing and if the spread is decreasing.  | In a up-trend. You can buy ! (it might be too early)
Else | Wait for buy..

#### Case 3
When the short term moving average (MMC) is crossing
the long term moving average (MML) from __below__.

![Case 3](/pictures/Case4.png)

Situation | Recommendation
------------ | -------------
If the long-term moving average (MML) is increasing and if the volume trend is higher than 50% | Buy Today!! (or Buy Now!!)
If the long-term moving average (MML) is increasing and if the volume trend is lower than 50% | You can buy but it's not a volume trend.
Else | Wait.

#### Case 4
When the short term moving average (MMC) is crossing
the long term moving average (MML) from __above__.

![Case 4](/pictures/Case3.png)

Situation | Recommendation
------------ | -------------
Case 4 fulfilled | Sell Today!! (or Sell Now!!)









