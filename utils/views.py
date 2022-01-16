from __future__ import annotations

from io import BytesIO
from typing import Type

import discord
from discord.ext import commands


# original code from https://github.com/Sly0511/TroveBot/blob/master/utils/buttons.py#L138-L152
class Traceback(discord.ui.View):
    """Exception view for error handler"""

    def __init__(self, ctx: commands.Context, exception: Type[Exception], timeout=60) -> None:
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.exception = exception

    @discord.ui.button(label="Show traceback", style=discord.ButtonStyle.danger, emoji="⚠️")
    async def show(self, button: discord.ui.Button, interaction: discord.Interaction) -> discord.Message:
        """Send a file containing the traceback"""
        await interaction.response.defer()
        await interaction.followup.send(
            file=discord.File(BytesIO(self.exception.encode("utf-8")), filename="exception.py")
        )
