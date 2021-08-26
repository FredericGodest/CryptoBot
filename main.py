"""
This module is sending message to discord channel with the message retrieved from crypto_data.py.
"""

import discord
from datetime import datetime
from dotenv import dotenv_values
import os
import crypto_data
import time

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
def get_crypto_info(interval : str, tweet: bool):
  """
  This function is preparing the message for discord.

  :param interval: This is the interval of the analysis. It can be 1d for one day or 1h for one hour.
  :param bool: This is defining if the tweet analysis has to be done or not.
  :return info: the message to send to discord channel
  """
  messages = crypto_data.get_status(interval, tweet)
  if tweet:
    info = '\n'.join(messages)
    return info
  else:
    info = ["Alerte(s) direct !"]
    for message in messages:
      if "Achetez aujourd'hui!! :sunny: " in message:
        message = message.replace("aujourd'hui", "tout de suite")
        info.append(message)
      elif "Vendez aujourd'hui!! :zap: " in message:
        message = message.replace("aujourd'hui", "tout de suite")
        info.append(message)
    info = '\n'.join(info)

    return info


#DISCORD PART
client = discord.Client()

@client.event
async def on_ready():
  print("Crypto Bot Connected !")
  memory = "nothing"  # memory for info alert
  while True:
    current_time_day = datetime.now().strftime("%H:%M:%S")
    current_time = datetime.now().strftime("%M:%S")

    #MORNING
    if str(current_time_day) == "06:30:00": #2 hours of delay
      info = get_crypto_info('1d', True)
      channel = client.get_channel(int(weekly_crypto))
      await channel.send("Tendance du jour #1")
      await channel.send(info)

    #EVENING
    elif str(current_time_day) == "17:30:30": #2 hours of delay
      info = get_crypto_info('1d', True)
      channel = client.get_channel(int(weekly_crypto))
      await channel.send("Tendance du jour #2")
      await channel.send(info)

    elif str(current_time) == "00:00": #Every Hours
      info = get_crypto_info('1d', False)
      channel = client.get_channel(int(weekly_crypto))
      if info != "Alerte(s) direct !":
        if info != memory: #if latest in not the same as the new one
          await channel.send(info)
          memory = info #save info into memory
      time.sleep(1)

client.run(bot_token)
