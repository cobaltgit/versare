from pathlib import Path

from discord.ext import commands

from utils.objects import BaseEmbed


class HelpEmbed(BaseEmbed):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_footer(
            text="Use help [command|category] for more information | <> denotes a required argument | [] denotes an optional argument"
        )

    def get_command_signature(self, command):
        if command.parent:
            return f"{self.context.prefix}{command.parent} {command.name} {command.signature}"
        return f"{self.context.prefix}{command.name} {command.signature}"


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
        self.code_lines = sum(1 for pyfile in Path(".").glob("**/*.py") for line in open(pyfile))

    async def send_command_help(self, command):
        embed = HelpEmbed(
            title=f"Help for command '{command}'",
            color=self.context.guild.me.color,
            description=command.description or command.brief or "Command not described",
        )
        embed.add_field(name="Usage", value=self.get_command_signature(command), inline=False)
        if command.aliases:
            embed.add_field(name="Aliases", value=", ".join(command.aliases), inline=False)
        if command._buckets and (cooldown := command._buckets._cooldown):
            embed.add_field(
                name="Cooldown", value=f"{cooldown.rate} use(s) per {cooldown.per:.0f} second(s)", inline=False
            )
        await self.context.send(embed=embed)

    async def send_group_help(self, group):
        embed = HelpEmbed(
            title=f"Help for group '{group}'",
            color=self.context.guild.me.color,
            description=group.description or group.brief or "Group not described",
        )
        embed.add_field(name="Usage", value=f"{self.context.prefix}{group.name} {group.signature}", inline=False)
        embed.add_field(
            name="Subcommands",
            value="\n".join(
                [
                    f"{self.get_command_signature(command)} - {command.brief}"
                    for idx, command in enumerate(group.commands)
                ]
            )
            or "No subcommands",
            inline=False,
        )
        if group.aliases:
            embed.add_field(name="Aliases", value=", ".join(group.aliases), inline=False)
        await self.context.send(embed=embed)

    async def send_cog_help(self, cog):
        embed = HelpEmbed(title=f"Help for cog '{cog.qualified_name}'", color=self.context.guild.me.color)
        embed.description = cog.description or "Cog not described"
        embed.add_field(
            name="Commands",
            value="\n".join(
                [f"{self.get_command_signature(command)} - {command.brief}" for command in cog.get_commands()]
            ),
        )
        await self.context.send(embed=embed)

    async def send_bot_help(self, mapping):
        embed = HelpEmbed(title="Versare Help", color=self.context.guild.me.color)
        for cog, commands in mapping.items():
            filtered = await self.filter_commands(commands, sort=True)

            commands = [self.get_command_signature(c) + f" - {c.brief}" for c in filtered]
            if commands:
                cog_name = getattr(cog, "qualified_name", "Uncategorised")
                embed.add_field(
                    name=cog_name + f" [{len(set(cog.walk_commands()))}]" if cog else cog_name,
                    value="\n".join(commands),
                    inline=False,
                )

        embed.description = f"""Written in {self.code_lines} lines of Python source code - this is yet to increase"""
        await self.context.send(embed=embed)

    async def send_error_message(self, error):
        await self.context.send(embed=BaseEmbed(title="Error", description=error, color=0x800000))
