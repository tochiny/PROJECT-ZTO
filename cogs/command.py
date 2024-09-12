import discord
import asyncio
from discord import Interaction, app_commands
from discord.ext import commands
from main import MyClient

class Command(commands.Cog):

    def __init__(self, client):
        self.client = client

    @app_commands.command(name="ping", description="check ping to serve")
    async def ping(self, interaction: Interaction):
        ping1 = f"{str(round(self.client.latency * 1000))} ms"
        await interaction.response.send_message(ping1)

    @app_commands.command(name="say", description="bot say too same")
    @app_commands.describe(word='Input word')
    async def say(self, interaction: Interaction, word: str):
        await interaction.response.send_message(word)


async def setup(client):
    await client.add_cog(Command(client))
