import discord
import google.generativeai as genai
import os


class Client(discord.Client):
    def __init__(self, intents):
        super().__init__(intents=intents)
        genai_api_key = os.getenv("GENAI_API_KEY")
        genai.configure(api_key=genai_api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    # initialize a gemini-1.5-flash object
    # genai.configure(api_key=genai_api_key)
    # model = genai.GenerativeModel("gemini-1.5-flash")

    async def on_ready(self):
        # discord bot is ready
        print(f'Logged in as {self.user}!')

    async def on_message(self, message):
        max_message_length = 1000
        print(f'Message received from {message.author}:{message.content}')
        print(f"Message Type: {type(message.content)}")

        # if user sends messages that calls bot
        if message.content.startswith('!genai'):
            user_input = message.content[6:]
            genai_response = self.model.generate_content(user_input)
            response = genai_response.text
            if len(response) > max_message_length:
                response = response[:max_message_length]
            await message.channel.send(response)
