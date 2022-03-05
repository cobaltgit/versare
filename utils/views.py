from __future__ import annotations

from io import StringIO
from typing import Type

import discord
from discord.ext import commands


# original code from https://github.com/Sly0511/TroveBot/blob/master/utils/buttons.py#L138-L152
# Copyright (c) 2018-2022 Cobalt, Sly, licensed under the MIT License
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
            file=discord.File(StringIO(self.exception), filename="exception.py"), ephemeral=True
        )


class Wordle(discord.ui.View):
    """View for Wordle game command"""

    def __init__(self, word: str) -> None:
        super().__init__()
        self.word = word

    @discord.ui.button(label="How to Play", style=discord.ButtonStyle.green, emoji="⌨️")
    async def instructions(self, button: discord.ui.Button, interaction: discord.Interaction) -> discord.Message:
        """Send official instructions on how to play"""
        await interaction.response.defer()
        return await interaction.followup.send(
            "To guess a word, type it in chat!",
            file=discord.File("utils/files/wordle_instructions.png"),
            ephemeral=True,
        )

    @discord.ui.button(label="Exit", style=discord.ButtonStyle.danger, emoji="❌")
    async def exit(self, button: discord.ui.Button, interaction: discord.Interaction) -> discord.Message:
        """Stop the view and game"""
        await interaction.response.send_message(f"Exited Wordle. The correct word was '{self.word}'")
        return self.stop()
