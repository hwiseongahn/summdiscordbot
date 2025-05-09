import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
from dotenv import load_dotenv
import asyncio
from itertools import cycle
import logging
import google.generativeai as genai
from modal import MessageCountModal

load_dotenv()
discord_token = os.getenv('DISCORD_TOKEN')
genai_api_key = os.getenv('GENAI_API_KEY')
genai.configure(api_key=genai_api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

logging.basicConfig(level=logging.INFO)
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
bot_statuses = cycle(["Made by Hwiseong 💻", "Made by Darsh 🧠"])
GUILD_ID = discord.Object(id=1319142553030885447)


@tasks.loop(seconds=5)
async def change_bot_status():
    await bot.change_presence(activity=discord.CustomActivity(name=next(bot_statuses)))


@bot.event
async def on_ready():
    print("Bot ready!")
    change_bot_status.start()

    try:
        synced_commands = await bot.tree.sync()
        print(f"Synced {len(synced_commands)} commands.")
    except Exception as e:
        print("Error trying to sync commands", e)


@bot.tree.command(name="hello", description="says hello FR")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"{interaction.user.mention} Hello there!")


@bot.tree.command(name="bye", description="says bye FR")
async def bye(interaction: discord.Interaction):
    await interaction.response.send_message(f"{interaction.user.mention} BYE!")


@bot.tree.command(name="summarize", description="summarize this conversation")
@app_commands.describe(msg_to_summ="How many previous messages should be summarized?", only_you_see="Only you can see the summary")
@app_commands.choices(only_you_see=[discord.app_commands.Choice(name="Yes", value=True), discord.app_commands.Choice(name="No", value=False)])
async def summarize(interaction: discord.Interaction, msg_to_summ: int, only_you_see: bool ):
    
    if msg_to_summ > 300:
        await interaction.response.send_message("cannot summarize more than 300 messages", ephemeral=True)
        return
    elif msg_to_summ < 1:
        await interaction.response.send_message("cannot summarize less than 1 message", ephemeral=True)
        return
    messages = [msg async for msg in interaction.channel.history(limit=msg_to_summ+1)]
    user_input = ''
    for msg in reversed(messages[1:]):  # reverse messages to get chronological order of msg
        user_input += f'{msg.author}: {msg.content}\n'
    user_input = "summarize this conversation:\n " + user_input
    print(user_input)
    genai_response = model.generate_content(user_input).text
    await interaction.response.send_message(f"{interaction.user.name} said to summarize the last {msg_to_summ} messages.", ephemeral=only_you_see)
    for i in range (0, len(genai_response), 2000):
        await interaction.channel.send(genai_response[i:i+2000], ephemeral=only_you_see)

#three dots on message > apps > context menu bot commands
@bot.tree.context_menu(name="Summarize after message")
async def summarize_from_here(interaction: discord.Interaction, message: discord.Message):
    await interaction.response.send_modal(MessageCountModal(message, True ))

@bot.tree.context_menu(name="Summarize before message")
async def summarize_from_here(interaction: discord.Interaction, message: discord.Message):
    await interaction.response.send_modal(MessageCountModal(message, False ))

async def main():
    async with bot:
        await bot.start(discord_token)

asyncio.run(main())
