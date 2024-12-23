import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv
import asyncio
from itertools import cycle
import logging

load_dotenv()
discord_token = os.getenv('DISCORD_TOKEN')
genai_api_key = os.getenv('GENAI_API_KEY')

logging.basicConfig(level=logging.INFO)
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
bot_statuses = cycle(["Status one", "Status two"])
GUILD_ID = discord.Object(id=1319142553030885447)


@tasks.loop(seconds=5)
async def change_bot_status():
    await bot.change_presence(activity=discord.Game(next(bot_statuses)))


@bot.event
async def on_ready():
    print("Bot ready!")
    change_bot_status.start()

    try:
        synced_commands = await bot.tree.sync(guild=GUILD_ID)
        print(f"Synced {len(synced_commands)} commands.")
    except Exception as e:
        print("Error trying to sync commands", e)


@bot.tree.command(name="hello", description="says hello FR", guild=GUILD_ID)
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"{interaction.user.mention} Hello there!")


@bot.tree.command(name="bye", description="says bye FR", guild=GUILD_ID)
async def bye(interaction: discord.Interaction):
    await interaction.response.send_message(f"{interaction.user.mention} BYE!")


@bot.command(name="hello")
async def hello_prefix(ctx):
    await ctx.send(f"{ctx.author.mention} Hello there!")


async def main():
    async with bot:
        await bot.start(discord_token)


asyncio.run(main())
