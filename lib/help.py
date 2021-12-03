import discord
from discord.ext import commands


class VersareHelp(commands.MinimalHelpCommand):
    def __init__(self):
        super().__init__(verify_checks=False)
