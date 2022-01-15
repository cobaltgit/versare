from __future__ import annotations
import discord

class BaseEmbed(discord.Embed):
    """Base embed class"""
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.timestamp = discord.utils.utcnow()
