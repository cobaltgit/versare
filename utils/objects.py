from datetime import datetime

import discord


class BaseEmbed(discord.Embed):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timestamp = datetime.utcnow()
