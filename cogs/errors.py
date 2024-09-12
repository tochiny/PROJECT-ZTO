import traceback
import discord
from discord import Interaction
from discord.app_commands import (
    AppCommandError,
    BotMissingPermissions,
    CommandNotFound as AppCommandNotFound,
    CommandOnCooldown,
    MissingPermissions,
)
from discord.ext import commands
from discord.ext.commands import BadLiteralArgument, CheckFailure, CommandNotFound, MissingRequiredArgument

class ErrorHandler(commands.Cog):
    def __init__(self, client):
        self.client = client
        client.tree.on_error = self.on_app_command_error

    async def on_app_command_error(self, interaction: Interaction, error: AppCommandError):
        traceback.print_exception(type(error), error, error.__traceback__)

async def setup(client):
    await client.add_cog(ErrorHandler(client))