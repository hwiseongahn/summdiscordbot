import discord
import openai
from dotenv import load_dotenv
import os
import logging
import asyncio

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
openai.api_key = os.getenv("OPENAI_API_KEY")

class Client(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user}!')

    async def on_message(self, message):
        # print(message)
        print(f'Message received from {message.author}:{message.content}')
        print(f"Message Type: {type(message.content)}")

        try:
            if message.content.startswith("!chatgpt"):
                # Extract the user's input after the command
                user_input = message.content[9:].strip()

                # Get a response from the ChatGPT API

                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",  # You can choose a model like "gpt-3.5-turbo" or "gpt-4"
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": user_input}
                    ],
                    max_tokens=100
                )

                # Send the response from ChatGPT back to Discord
                await message.channel.send(response.choices[0].text.strip())
        except Exception as e:
            logging.error(f"Error processing message: {e}")
            # Optionally, print more details
            raise  # Re-raise the exception to get the full traceback
        if message.content.startswith("!chatgpt"):
            # Extract the user's input after the command
            user_input = message.content[9:]

            # Get a response from the ChatGPT API
            response = openai.Completion.create(
                engine="text-davinci-003",  # You can choose the model (e.g., text-davinci-003)
                prompt=user_input,
                max_tokens=150
            )

            # Send the response from ChatGPT back to Discord
            await message.channel.send(response.choices[0].text.strip())

            await asyncio.sleep(1)  # 1 second delay between requests


intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = Client(intents=intents)
client.run(token)
