import discord
from dotenv import load_dotenv
from client import Client
import os

# load api keys from the env file
load_dotenv()
token = os.getenv('DISCORD_TOKEN')
genai_api_key = os.getenv("GENAI_API_KEY")


# set intents to allow receiving messages
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
# initialize a discord client object
client = Client(intents=intents)
client.run(token)
