import discord
import google.generativeai as genai
import os


# given response, if greater than 2000 characters truncate it
async def truncateLongMessage(response):
    max_message_length = 2000  # messages can't exceed 2000 in discord
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

    async def on_ready(self):  # discord bot is ready
        print(f'Logged in as {self.user}!')

    async def on_message(self, message):

        response = "Error"  # have a default response of Error (easier to debug)

        if message.author == self.user:  # if the message is from the bot, do nothing
            return

        max_summ_length = 150  # don't summarize more messages than 150
        print(f'Message received from {message.author}: {message.content}')

        if message.content.startswith('!genai'):  # if user wants to use genai
            user_input = message.content[6:]
            if user_input == "":  # if user gives empty prompt
                response += ", user gave empty statement"  # append reason of error, to error msg
                await message.channel.send(response)

            genai_response = self.model.generate_content(user_input)  # generate content with user prompt
            if genai_response.candidates[0].finish_reason.value == 4:  # if genai gives an error for copyright
                response = "Gemini came across copyright issues"
                await message.channel.send(response)  # send response explaining error
                return

        elif message.content.startswith('!last'):  # if user wants to summarize last few messages
            user_input = message.content[5:]  # exclude user saying '!last' from input
            num_of_msg = 0

            for i in range(0, 3):  # loop through the next 3 characters the user sent
                try:
                    num_of_msg += int(user_input[i]) * pow(10, 2 - i)
                except ValueError:  # catch error when user uses command without an int
                    await message.channel.send("input was not an integer")
                    return
                except IndexError:  # if num of msgs to summ was less than 3 characters long
                    num_of_msg /= pow(10, 2 - i)
                    num_of_msg = int(num_of_msg)
                    break
            if num_of_msg > max_summ_length:  # catch error for input > 150 summarized messages
                await message.channel.send(f"cannot summarize {num_of_msg}, try 150 or less.")
                return
            # Fetch the last few messages from the channel
            messages = [msg async for msg in message.channel.history(limit=num_of_msg + 1)]

            # Iterate over the messages and append to one string
            user_input = ''
            for msg in reversed(messages[1:]):  # reverse messages to get chronological order of msg
                user_input += f'{msg.author}: {msg.content}\n'
            user_input = "summarize this conversation: " + user_input
            print(user_input)  # for debugging

        # else, if user input isn't an existing command, do nothing
        else:
            return

        # since user's message is a command, generate content, send msg given the user input
        genai_response = self.model.generate_content(user_input)
        response = genai_response.text
        response = await truncateLongMessage(response)
        await message.channel.send(response)
