from datetime import datetime

import discord
from discord.ext import commands


class VersareHelp(commands.MinimalHelpCommand):
    def __init__(self):
        super().__init__(
            verify_checks=False,
            command_attrs={
                "name": "help",
                "aliases": ["plshelp", "helpme", "assistance"],
                "cooldown": commands.CooldownMapping.from_cooldown(2, 5, commands.BucketType.user),
            },
        )

    async def send_command_help(self, command):
        embed = discord.Embed(
            title=f"Help for command '{command}'",
            color=self.context.guild.me.color,
            description=command.description,
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="Usage", value=self.get_command_signature(command), inline=False)
        if command.aliases:
            embed.add_field(name="Aliases", value=", ".join(command.aliases), inline=False)
        if command._buckets and (cooldown := command._buckets._cooldown):
            embed.add_field(name="Cooldown", value=f"{cooldown.rate} uses per {cooldown.per:.0f} seconds", inline=False)
        await self.context.send(embed=embed)

    async def send_group_help(self, group):
        embed = discord.Embed(
            title=f"Help for group '{group}'",
            color=self.context.guild.me.color,
            description=group.description,
            timestamp=datetime.utcnow(),
        )
        embed.set_footer(text=f"Get help on subcommands by using {self.context.prefix}help [GROUP] [COMMAND]")
        embed.add_field(name="Usage", value=f"{self.context.prefix}{group.name} {group.signature}", inline=False)
        embed.add_field(
            name="Subcommands",
            value="\n".join(
                [f"{self.context.prefix}{command.name} - {command.brief}" for idx, command in enumerate(group.commands)]
            )
            or "No subcommands",
            inline=False,
        )
        if group.aliases:
            embed.add_field(name="Aliases", value=", ".join(group.aliases), inline=False)
        await self.context.send(embed=embed)

    async def send_cog_help(self, cog):
        embed = discord.Embed(
            title=f"Help for cog '{cog.qualified_name}'", color=self.context.guild.me.color, timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"Get help on individual commands by using {self.context.prefix}help [COMMAND]")
        embed.add_field(
            name="Commands",
            value="\n".join(
                [f"{self.context.prefix}{command.name} - {command.brief}" for command in cog.get_commands()]
            ),
        )
        await self.context.send(embed=embed)

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Versare Help", color=self.context.guild.me.color, timestamp=datetime.utcnow())
        embed.description = f"""To get information on a command, use `{self.context.prefix}help [COMMAND]`
            For categories (cogs), use `{self.context.prefix}help [CATEGORY]`"""
        for cog, commands in mapping.items():
            filtered = await self.filter_commands(commands, sort=True)
            commands = [self.get_command_signature(c) + f" - {c.brief}" for c in filtered]
            if commands:
                cog_name = getattr(cog, "qualified_name", "Uncategorised")
                embed.add_field(name=cog_name, value="\n".join(commands), inline=False)

        await self.context.send(embed=embed)

    async def send_error_message(self, error):
        await self.context.send(
            embed=discord.Embed(title="Error Message", description=error, color=0x800000, timestamp=datetime.utcnow())
        )
