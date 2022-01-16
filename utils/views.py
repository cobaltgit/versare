from __future__ import annotations

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
        """Send first 4000 characters of exception - in the future, this will send a file"""
        if len(self.exception) > 2000:
            await interaction.response.send_message(f"```py\n{self.exception[:1990]}```", ephemeral=True)
            await interaction.followup.send(f"```py\n{self.exception[1990:3980]}```", ephemeral=True)
        else:
            await interaction.response.send_message(f"```py\n{self.exception}```", ephemeral=True)
