from datetime import datetime
from random import choice

import discord
from discord.ext import commands
from discord.ui import View, button


class RPSView(View):
    def __init__(self, ctx):
        self.ctx = ctx
        self.user = self.ctx.author
        super().__init__(timeout=15)

    async def process(self, rps_user: str):
        rps_cpu = choice(["rock", "paper", "scissors"])
        checks = {
            ("rock", "scissors"): "win",
            ("scissors", "rock"): "loss",
            ("paper", "scissors"): "loss",
            ("paper", "rock"): "win",
            ("rock", "paper"): "loss",
            ("scissors", "paper"): "win",
        }
        result = checks[(rps_user, rps_cpu)] if rps_user != rps_cpu else "draw"
        if result == "win":
            embed = discord.Embed(title="You won!", color=0x50C878, timestamp=datetime.utcnow())
            emoji_url = (
                "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/twitter/282/trophy_1f3c6.png"
            )
        elif result == "loss":
            embed = discord.Embed(title="You lost!", color=0xD22B2B, timestamp=datetime.utcnow())
            emoji_url = (
                "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/twitter/282/stop-sign_1f6d1.png"
            )
        elif result == "draw":
            embed = discord.Embed(title="It's a tie!", color=0xFFBF00, timestamp=datetime.utcnow())
            emoji_url = (
                "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/twitter/282/necktie_1f454.png"
            )
        fields = [("Your choice", rps_user.title(), True), ("CPU's choice", rps_cpu.title(), True)]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        embed.set_thumbnail(url=emoji_url)
        await self.message.edit(embed=embed, view=None)
        self.stop()

    @button(label="Rock", style=discord.ButtonStyle.red, emoji="🪨")
    async def callback1(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user != self.user:
            return
        return await self.process("rock")

    @button(label="Paper", style=discord.ButtonStyle.green, emoji="📄")
    async def callback2(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user != self.user:
            return
        return await self.process("paper")

    @button(label="Scissors", style=discord.ButtonStyle.blurple, emoji="✂️")
    async def callback3(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user != self.user:
            return
        return await self.process("scissors")

    async def on_timeout(self):
        await self.ctx.send("Game timeout reached", ephemeral=True)
        self.stop()
