import discord
import google.generativeai as genai
import os


async def truncateLongMessage(max_message_length, response):
    if len(response) > max_message_length:  # if message exceeds discord's limit, cut it
        print("long response!")  # prints to terminal that message exceeded discord limit
        response = response[:max_message_length]
    return response


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

        max_message_length = 2000  # messages can't exceed 2000 in discord
        max_summ_length = 150  # don't summarize more messages than 150
        print(f'Message received from {message.author}: {message.content}')

        # if user wants to use genai
        if message.content.startswith('!genai'):
            user_input = message.content[6:]
            if user_input == "":
                # append to error message that user gave empty statement
                response += ", user gave empty statement"
                # response = "error" above, so it sends that if there's an issue (blank space)
                await message.channel.send(response)

            genai_response = self.model.generate_content(user_input)
            if genai_response.candidates[0].finish_reason.value == 4:  # if genai gives an error for any reason
                response = "Gemini came across copyright issues"
                await message.channel.send(response)  # send response explaining error
                return
        # if user wants to summarize last 5 messages
        elif message.content.startswith('!last'):
            user_input = message.content[5:]
            num_of_msg = 0
            # make sure the input that comes after '!last' is an int
            for i in range(0, 3):
                try:
                    num_of_msg += int(user_input[i]) * pow(10, 2 - i)
                except ValueError:  # catch error for when user doesn't input an int
                    await message.channel.send("input was not an integer")
                    return
                except IndexError:
                    break
            if num_of_msg > max_summ_length:  # catch error for input > 150 summarized messages
                await message.channel.send(f"cannot summarize {num_of_msg}, try 150 or less.")
                return
            # Fetch the last 5 messages from the channel
            messages = [msg async for msg in message.channel.history(limit=num_of_msg + 1)]

            # Iterate over the messages and make them one string
            user_input = ''
            for msg in reversed(messages[1:]):  # reverse messages to get chronological order of msg
                user_input += f'{msg.author}: {msg.content}\n'
            user_input = "summarize this conversation: " + user_input
            print(user_input)

        # if user's message isn't a command, do nothing
        else:
            return

        # since user's message is a command, generate content, given the user input
        genai_response = self.model.generate_content(user_input)
        response = genai_response.text
        response = await truncateLongMessage(max_message_length, response)
        await message.channel.send(response)
