from datetime import datetime

import discord
from discord.ext import commands


class VersareHelp(commands.MinimalHelpCommand):
    def __init__(self):
        super().__init__(verify_checks=False)

    async def send_command_help(self, command):
        embed = discord.Embed(
            title=f"Help for command '{command}'",
            color=self.context.guild.me.color,
            description=command.description,
            timestamp=datetime.utcnow(),
        )
        if command.parent:
            embed.add_field(
                name="Usage",
                value=f"{self.context.prefix}{command.full_parent_name} {command.name} {command.signature}",
                inline=False,
            )
        else:
            embed.add_field(
                name="Usage", value=f"{self.context.prefix}{command.name} {command.signature}", inline=False
            )
        await self.context.send(embed=embed)

    async def send_group_help(self, group):
        embed = discord.Embed(
            title=f"Help for group '{group}'",
            color=self.context.guild.me.color,
            description=group.description,
            timestamp=datetime.utcnow(),
        )
        embed.set_footer(text=f"Get help on subcommands by using {self.context.prefix}help <group-name> <command-name>")
        embed.add_field(name="Usage", value=f"{self.context.prefix}{group.name} {group.signature}", inline=False)
        embed.add_field(
            name="Subcommands",
            value="\n".join(
                [f"{self.context.prefix}{command.name} - {command.brief}" for idx, command in enumerate(group.commands)]
            )
            or "No subcommands",
            inline=False,
        )
        await self.context.send(embed=embed)

    async def send_cog_help(self, cog):
        embed = discord.Embed(
            title=f"Help for cog '{cog.qualified_name}'", color=self.context.guild.me.color, timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"Get help on individual commands by using {self.context.prefix}help <command-name>")
        embed.add_field(
            name="Commands",
            value="\n".join(
                [f"{self.context.prefix}{command.name} - {command.brief}" for command in cog.get_commands()]
            ),
        )
        await self.context.send(embed=embed)
