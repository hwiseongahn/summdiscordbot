import discord
from discord.ui import Modal, TextInput
from discord import TextStyle
import google.generativeai as genai
import os
from dotenv import load_dotenv
import google.generativeai as genai


class MessageCountModal(Modal, title="Summarize Messages"):
    def __init__(self, message: discord.Message):
        genai_api_key = os.getenv("GENAI_API_KEY")
        genai.configure(api_key=genai_api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        super().__init__()
        self.message = message  # Store the starting message

        # Text input for number of messages
        self.message_count = TextInput(
            label="How many messages to summarize (1–100)",
            placeholder="Enter a number like 25",
            required=True,
            min_length=1,
            max_length=3,
            style=TextStyle.short
        )

        self.add_item(self.message_count)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            count = int(self.message_count.value)
            if not (1 <= count <= 100):
                raise ValueError("Count out of range")
        except ValueError:
            await interaction.response.send_message("Invalid number. Enter a number between 1 and 100.", ephemeral=True)
            return

        messages = [msg async for msg in interaction.channel.history(limit=count + 1)]
        user_input = ''
        for msg in reversed(messages[1:]):  # reverse messages to get chronological order of msg
            user_input += f'{msg.author}: {msg.content}\n'
            user_input = "summarize this conversation:\n " + user_input
        print(user_input)
        genai_response = self.model.generate_content(user_input).text
        await interaction.response.send_message(f"{interaction.user.name} said to summarize the next {count} messages.`")
        
        for i in range (0, len(genai_response), 2000):
            await interaction.channel.send(genai_response[i:i+2000])