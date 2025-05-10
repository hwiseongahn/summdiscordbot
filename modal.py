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

        self.public_choice = TextInput(
            label="Send summary to channel?",
            placeholder="Leave blank for yes, or enter 'y'/'n'",
            required=False,
            min_length=1,
            max_length=2,
            style=TextStyle.short
        )
        self.add_item(self.public_choice)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            count = int(self.message_count.value)
            if not (1 <= count <= 300):
                raise ValueError("Count out of range")
            send_summ = self.public_choice.value.lower() if self.public_choice.value else "yes"
            if send_summ not in ["yes", "y", "no", "n"]:
                raise ValueError("Invalid choice. Leave blank for yes, or enter 'y' or 'n'")
        except ValueError as e:
            if str(e) == "Count out of range":
                await interaction.response.send_message("Invalid number. Enter a number between 1 and 300.", ephemeral=True)
            elif str(e) == "Invalid choice. Leave blank for yes, or enter 'y' or 'n'":
                await interaction.response.send_message("Invalid choice. Leave blank for yes, or enter 'y' or 'n'.", ephemeral=True)
            else:
                await interaction.response.send_message("An unexpected error occurred.", ephemeral=True)
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
        direction = "next" if self.summ_after else "previous"
        genai_response = f"`summary of the {direction} {count} messages:`" + "\n\n" + genai_response
        
        for i in range (0, len(genai_response), 2000):
            await interaction.response.send_message(genai_response[i:i+2000], ephemeral=(send_summ.lower() in ["no", "n"]))