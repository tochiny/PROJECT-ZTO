import discord
import asyncio
import aiohttp
import time
import traceback
import os
from discord import app_commands
from discord.ext import commands, tasks
from cogs import command, manhwa, errors
from tool import database
from tool import organize
from tool import GetManhawa
from myserver import server_on

PREFIX = "/"

COGS = ["cogs.command", "cogs.manhwa", "cogs.errors"]
intents = discord.Intents.default()
intents.message_content = True


class MyClient(commands.Bot):

    def __init__(self):
        super().__init__(command_prefix=PREFIX, intents=intents)
        self.session: aiohttp.ClientSession = None
        self.token = os.getenv("TOKEN")
        self.cogs_list = COGS
        self.database_path = "data/list.json"
        self.text_path = "data/backup_database.txt"
        self.data = database.DataBase(self)
        self.database = self.data.database
        self.getMangawa = GetManhawa()
        self.organize = organize.Organize()

    async def on_ready(self):
        print("[ PROJECT CODE NAME 'ZTO' ]")
        print(f"[ USERNAME ]: {self.user}")
        print("Login success")
        try:
            await self.tree.sync()
        except:
            traceback.print_exc()

    async def setup_hook(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()
        await self.load_cogs()

    async def load_cogs(self):
        for cogs_ in self.cogs_list:
            try:
                await self.load_extension(cogs_)
            except:
                traceback.print_exc()

    async def close(self):
        await self.session.close()
        await super().close()

    async def start(self):
        return await super().start(self.token, reconnect=True)


server_on()

client = MyClient()
asyncio.run(client.start())
