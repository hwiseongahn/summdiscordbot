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

        response = "Error"  # have a default response of Error (easier to debug)

        if message.author == self.user:  # if the message is from the bot, do nothing
            return

        channel_id = message.channel.id
        channel = self.get_channel(channel_id)
        max_message_length = 2000  # messages can't exceed 2000 in discord
        print(f'Message received from {message.author}: {message.content}')

        user_input = ""  # user input is initially empty

        # if user wants to use genai
        if message.content.startswith('!genai'):
            user_input = message.content[6:]
            if user_input == "":
                # append to error message that user gave empty statement
                response += ", user gave empty statement"
                # response = "error" above, so it sends that if there's an issue (blank space)
                await message.channel.send(response)

            genai_response = self.model.generate_content(user_input)
            if genai_response.candidates:  # if genai gives an error for any reason
                response = genai_response.candidates[0]
                await message.channel.send(response)  # send response explaining error
            else:
                response = genai_response.text

        # if user wants to summarize last 5 messages
        elif message.content.startswith('!last5'):
            # Fetch the last 5 messages from the channel
            messages = [msg async for msg in message.channel.history(limit=5)]

            # Iterate over the messages and make them one string
            user_input = ''
            for msg in reversed(messages):  # reverse messages to get chronological order of msg
                user_input += f'{msg.author}: {msg.content}\n'
            user_input = "summarize this conversation: " + user_input

        # if user's message isn't a command, do nothing
        else:
            return

        # since user's message is a command, generate content, given the user input
        genai_response = self.model.generate_content(user_input)
        response = genai_response.text
        if len(response) > max_message_length:  # if message exceeds discord's limit, cut it
            print("long response!")  # prints to terminal that message exceeded discord limit
            response = response[:max_message_length]
        await message.channel.send(response)
