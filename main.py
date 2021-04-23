import discord
import crypto_data
from datetime import datetime
from dotenv import dotenv_values
import os

#CONFIG ENV PART
try:
  config = dotenv_values(".env")
except:
  print("env not found")

if os.environ.get("ENV") == "PROD":
  bot_token = os.environ.get("TOKEN_BOT")
  channel_general = os.environ.get("channel_general")
  dev_crypto = os.environ.get("dev_crypto")
else:
  bot_token = config['TOKEN_BOT']
  channel_general = config['channel_general']
  dev_crypto = config['dev_crypto']

CHANNELS = [channel_general, dev_crypto]

#GET DATA PART
def get_crypto_info(interval):
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
    current_time_hour = datetime.now().strftime("%M:%S")

    #EVERY HOURS
    if str(current_time_hour) == "00:00":
      info = get_crypto_info('1h')
      print("direct info")
      if info:
        for i in range(0, len(CHANNELS)):
          channel = client.get_channel(int(CHANNELS[i]))
          await channel.send("Place au crypto-direct !")
          await channel.send(info)

    #MORNING
    if str(current_time_day) == "06:30:00": #2 hours of delay
      info = get_crypto_info('1d')
      for i in range(0, len(CHANNELS)):
        channel = client.get_channel(int(CHANNELS[i]))
        await channel.send("Tendance du jour #1")
        await channel.send(info)

    #EVENING
    elif str(current_time_day) == "15:30:00": #2 hours of delay
      info = get_crypto_info('1d')
      for i in range(0,len(CHANNELS)):
        channel = client.get_channel(int(CHANNELS[i]))
        await channel.send("Tendance du jour #2")
        await channel.send(info)

client.run(bot_token)
