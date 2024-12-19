import discord
import google.generativeai as genai
import os


class Client(discord.Client):
    def __init__(self, intents):
        super().__init__(intents=intents)
        genai_api_key = os.getenv("GENAI_API_KEY")
        genai.configure(api_key=genai_api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")


    async def on_ready(self):
        # discord bot is ready
        print(f'Logged in as {self.user}!')

    async def on_message(self, message):
        channel_id = message.channel.id
        channel = self.get_channel(channel_id)
        max_message_length = 2000
        print(f'Message received from {message.author}:{message.content}')
        print(f"Message Type: {type(message.content)}")

        user_input = ""
        # if user wants to use genai
        if message.content.startswith('!genai'):
            user_input = message.content[6:]
            genai_response = self.model.generate_content(user_input)
            response = genai_response.text
        # if user wants to summarize last 5 messages

        elif message.content.startswith('!last5'):
            # Fetch the last 5 messages from the channel
            messages = [msg async for msg in message.channel.history(limit=5)]

            # Iterate over the messages and make them one string
            user_input = ''
            for msg in messages:
                user_input += f'{msg.author}: {msg.content}\n'
            user_input = "summarize this conversation: " + user_input

        # if it isn't a command, do nothing
        else:
            return
        # now generate content, given the user input
        genai_response = self.model.generate_content(user_input)
        response = genai_response.text
        if len(response) > max_message_length:
            print("long response!")
            response = response[:max_message_length]
        await message.channel.send(response)
