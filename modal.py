import discord
from discord.ui import Modal, TextInput
from discord import TextStyle
import google.generativeai as genai
import os
import google.generativeai as genai


class MessageCountModal(Modal, title="Summarize Messages"):
    def __init__(self, message: discord.Message, summ_after: bool):
        genai_api_key = os.getenv("GENAI_API_KEY")
        genai.configure(api_key=genai_api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        super().__init__()
        self.message = message  # Store the starting message
        self.summ_after = summ_after

        # Text input for number of messages
        self.message_count = TextInput(
            label="How many messages to summarize (1–300)",
            placeholder="Enter a postive integer",
            required=True,
            min_length=1,
            max_length=3,
            style=TextStyle.short
        )

        self.add_item(self.message_count)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            count = int(self.message_count.value)
            if not (1 <= count <= 300):
                raise ValueError("Count out of range")
        except ValueError:
            await interaction.response.send_message("Invalid number. Enter a number between 1 and 300.", ephemeral=True)
            return
        print (count)
        if self.summ_after:
            messages = [self.message] + [msg async for msg in interaction.channel.history(after=self.message, limit=count - 1)]
        else:
            messages = [msg async for msg in interaction.channel.history(limit=count)]
        
        user_input = ''

        if self.summ_after:
            for msg in (messages):  # iterate in reverse to get chronological order of msg if summ_after true
                user_input += f'{msg.author}: {msg.content}\n'
        else:
            for msg in reversed(messages):  # iterate in reverse to get chronological order of msg if summ_after true
                user_input += f'{msg.author}: {msg.content}\n'
        
        user_input = "summarize this conversation:\n " + user_input
        print(user_input)
        genai_response = self.model.generate_content(user_input).text
        await interaction.response.send_message(f"{interaction.user.name} said to summarize the next {count} messages.`")
        
        for i in range (0, len(genai_response), 2000):
            await interaction.channel.send(genai_response[i:i+2000])