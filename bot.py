import discord  # py-cord 2.6.1
from dotenv import load_dotenv


class My_Bot:

    def __init__(self, on_ready, on_ready_args) -> None:
        # Set up bot
        load_dotenv()  # load all the variables from the env file
        self.bot = None
        self.on_ready = on_ready
        self.on_ready_args = on_ready_args

    def initialize(self, loop):
        self.bot = discord.Bot(loop=loop)

        for cog in ["cogs.game", "cogs.costs", "cogs.char", "cogs.session"]:
            self.bot.load_extension(cog)

        @self.bot.event
        async def on_ready():
            self.on_ready(*self.on_ready_args)

    async def close(self):
        self.bot.clear()
        await self.bot.close()
        exit()
