import discord


class Client(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user}!')

    async def on_message(self, message):
        print(message)
        print(f'Message received from {message.author}:{message.content}.')
        print(f"Message Type: {type(message.content)}")


intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = Client(intents=intents)
client.run('MTI5MzM5NDM0MzI5NzY3OTM5MA.GRZDIi.c_aeSMPZsJiPtZo7-r0Yo1zan7GJ1QIu4KMR0U')
