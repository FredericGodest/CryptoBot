import discord
import requests
import json
from deep_translator import GoogleTranslator
import crypto_data
import time

def read_token():
  with open("token.txt", 'r') as f:
    lines = f.readlines()
    return lines[0].strip()

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


def get_quote():
  response = requests.get("https://api.chucknorris.io/jokes/random")
  json_data = json.loads(response.text)
  quote = json_data['value']
  translated = GoogleTranslator(source='en' ,target='fr').translate(quote)
  return(quote, translated)


token = read_token()
client = discord.Client()
channel_general = 833746743165714475

@client.event
async def on_ready():
  print("Crypto bot ready !")

  while True:
    info = get_crypto_info('1h')
    channel = client.get_channel(channel_general)
    time.sleep(60*60)
    await channel.send(info)


@client.event
async def on_message(message):
  if message.author == client:
    return

  if message.content.startswith('BOT'):
    await message.channel.send('Hello !')

  if message.content.startswith('Chuck'):
    if message.author != client:
      quote, translated = get_quote()
      await message.channel.send("english: " + quote)
      await message.channel.send("traduction: " + translated)

  if message.content.startswith('DailyCrypto'):
    if message.author != client:
      info = get_crypto_info('1d')
      await message.channel.send(info)

  if message.content.startswith('HourCrypto'):
    if message.author != client:
      info = get_crypto_info('1h')
      await message.channel.send(info)


#keep_alive()
client.run(token)
