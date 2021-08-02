"""
This module is sending message to discord channel with the message retrieved from crypto_data.py.
"""

import discord
from datetime import datetime
from dotenv import dotenv_values
import os
import crypto_data

#PROD MOD
if os.environ.get("ENV") == "PROD":
  bot_token = os.environ.get("TOKEN_BOT")
  daily_crypto = os.environ.get("daily_crypto")
  weekly_crypto = os.environ.get("weekly_crypto")

#TEST MOD
else:
  config = dotenv_values(".env")
  bot_token = config['TOKEN_BOT']
  daily_crypto = config['channel_general']
  weekly_crypto = config['channel_general']

#GET DATA PART
def get_crypto_info(interval : str):
  """
  This function is preparing the message for discord.

  :param interval: This is the interval of the analysis. It can be 1d for one day or 1h for one hour.
  :return info: the message to send to discord channel
  """
  messages = crypto_data.get_status(interval)
  if interval == '1d':
    info = '\n'.join(messages)
    return info
  else:
    info = []
    for message in messages:
      if "Buy Today!!" in message:
        message = message.replace("Today", "Now")
        info.append(message)
      elif "Sell Today!!" in message:
        message = message.replace("Today", "Now")
        info.append(message)
    info = '\n'.join(info)

    return info


#DISCORD PART
client = discord.Client()
@client.event
async def on_ready():
  print("Crypto Bot Connected !")
  while True:
    current_time_day = datetime.now().strftime("%H:%M:%S")

    #MORNING
    if str(current_time_day) == "06:30:00": #2 hours of delay
      info = get_crypto_info('1d')
      channel = client.get_channel(int(weekly_crypto))
      await channel.send("Tendance du jour #1")
      await channel.send(info)

    #EVENING
    elif str(current_time_day) == "15:30:00": #2 hours of delay
      info = get_crypto_info('1d')
      channel = client.get_channel(int(weekly_crypto))
      await channel.send("Tendance du jour #2")
      await channel.send(info)

client.run(bot_token)
