import asyncio
import re
from io import BytesIO
from random import shuffle
from typing import Optional

import discord
import wavelink
from discord.ext import commands

import db.dj
from utils.objects import BaseEmbed, VersarePlayer


class Music(commands.Cog):
    """Long-awaited music commands!"""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.bot.loop.create_task(self.init_nodes())
        self.YT_REGEX = re.compile(
            r"^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$"
        )
        self.SC_REGEX = re.compile(r"^(?:(https?):\/\/)?(?:(?:www|m)\.)?(soundcloud\.com|snd\.sc)\/(.*)$")

    async def init_nodes(self) -> None:
        await self.bot.wait_until_ready()
        await wavelink.NodePool.create_node(bot=self.bot, **self.bot.config["lavalink"])
        self.node = wavelink.NodePool.get_node(identifier=self.bot.config["lavalink"]["identifier"])

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node) -> None:
        print(f"Lavalink node {node.identifier} ready")

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: VersarePlayer, track, reason):

        if all(m.bot for m in player.channel.members):
            return await player.disconnect()

        if player.loop and player.track is not None:
            return await player.play(player.track)
        else:
            await player.stop()

        player.wait_task = self.bot.loop.create_task(player.wait_for_next())

    @commands.group(
        name="play",
        aliases=["p"],
        brief="Play music in the current voice channel",
        description="Play music in the current voice channel, and connect to it if not present",
        invoke_without_command=True,
    )
    async def play(
        self,
        ctx,
    ) -> discord.Message:

        return await ctx.send_help("play")

    @play.command(
        name="youtube", aliases=["yt"], brief="Play YouTube tracks", description="Search and play YouTube tracks"
    )
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def play_youtube(
        self, ctx: commands.Context, *, query: str = commands.Option(description="Enter a query for YouTube tracks")
    ) -> discord.Message:

        embed = BaseEmbed(color=ctx.guild.me.color)
        track_search = None
        track = None

        async with ctx.channel.typing():
            if self.YT_REGEX.match(query):
                try:
                    if not hasattr(self, "node"):
                        return await ctx.send("Lavalink node is offline")
                    if "playlist" in query:
                        track = await self.node.get_playlist(query, wavelink.YouTubePlaylist)
                    else:
                        track = (await self.node.get_tracks(query=query, cls=wavelink.SoundCloudTrack))[0]
                except wavelink.errors.LavalinkException as e:
                    return await ctx.send(e)
            else:
                track_search = await wavelink.YouTubeTrack.search(query)

        if track_search:
            search_embed = BaseEmbed(
                title=f"First {len(track_search[:10])} results",
                description=(
                    "**I found the following tracks on __YouTube__:**\n\n"
                    + "\n".join(f"{idx+1}. '{val}' by '{val.author}'" for idx, val in enumerate(track_search[:10]))
                ),
                color=ctx.guild.me.color,
            )

            await ctx.send(embed=search_embed)

            try:
                response = await self.bot.wait_for(
                    "message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel
                )
            except asyncio.TimeoutError:
                return await ctx.send("Sorry, this command timed out. Please try again")
            except ValueError:
                return await ctx.send("Must provide a value between 1 and 10. Please try again")
            try:
                if int(response.content) not in range(1, 11):
                    return await ctx.send("Must provide a value between 1 and 10. Please try again")
            except (ValueError, TypeError):
                return await ctx.send("Must provide a value between 1 and 10. Please try again")

            track = track_search[int(response.content) - 1]

            embed.set_thumbnail(url=track.thumbnail)

        vc: VersarePlayer = ctx.voice_client or await self.initialise_voice_client(ctx.author.voice.channel)

        try:
            vc.wait_task.cancel()
        except:
            pass

        if isinstance(track, wavelink.YouTubePlaylist):
            if vc.is_playing():
                for pl_track in track.tracks:
                    await vc.queue.put_wait(pl_track)
            else:
                await vc.play(track.tracks[0])
                for pl_track in track.tracks[1:]:
                    await vc.queue.put_wait(pl_track)
            embed.title = "Queued Playlist"
        elif vc.is_playing():
            await vc.queue.put_wait(track)
            embed.title = "Added to Queue"
        else:
            await vc.play(track)
            embed.title = "Now Playing"

        if isinstance(track, wavelink.YouTubePlaylist):
            fields = [
                ("Source", "**YouTube**", True),
                ("Title", f"**{track.name}**", True),
            ]
            embed.set_thumbnail(url=track.tracks[0].thumbnail)
        else:
            fields = [
                ("Source", "**YouTube**", True),
                ("Title", f"**{track}**", True),
                ("Author", f"**{track.author}**", True),
            ]

            if isinstance(track, wavelink.YouTubeTrack):
                embed.set_thumbnail(url=track.thumbnail)
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        return await ctx.send(embed=embed)

    @play.command(
        name="soundcloud",
        aliases=["sc"],
        brief="Play SoundCloud tracks",
        description="Search and play SoundCloud tracks",
    )
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def play_soundcloud(
        self, ctx: commands.Context, *, query: str = commands.Option(description="Enter a query for SoundCloud tracks")
    ) -> discord.Message:

        embed = BaseEmbed(color=ctx.guild.me.color)
        track_search = None
        track = None

        async with ctx.channel.typing():
            if self.SC_REGEX.match(query):
                try:
                    if hasattr(self, "node"):
                        track = (await self.node.get_tracks(query=query, cls=wavelink.SoundCloudTrack))[0]
                    else:
                        return await ctx.send("Lavalink node is offline")
                except wavelink.errors.LavalinkException as e:
                    return await ctx.send(e)
            else:
                track_search = await wavelink.SoundCloudTrack.search(query)

            if track_search:
                search_embed = BaseEmbed(
                    title="First 10 results",
                    description=(
                        "**I found the following tracks on __SoundCloud__:**\n\n"
                        + "\n".join(f"{idx+1}. '{val}' by '{val.author}'" for idx, val in enumerate(track_search[:10]))
                    ),
                    color=ctx.guild.me.color,
                )

                await ctx.send(embed=search_embed)

            try:
                response = await self.bot.wait_for(
                    "message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel
                )
            except asyncio.TimeoutError:
                return await ctx.send("Sorry, this command timed out. Please try again")
            except ValueError:
                return await ctx.send("Must provide a value between 1 and 10. Please try again")
            try:
                if int(response.content) not in range(1, 11):
                    return await ctx.send("Must provide a value between 1 and 10. Please try again")
            except (ValueError, TypeError):
                return await ctx.send("Must provide a value between 1 and 10. Please try again")

            track = track_search[int(response.content) - 1]

            vc: wavelink.Player = ctx.voice_client or await self.ensure_voice(ctx)
            vc.loop = False

            try:
                vc.wait_task.cancel()
            except:
                pass

        if vc.is_playing():
            await vc.queue.put_wait(track)
            embed.title = "Added to Queue"
        else:
            await vc.play(track)
            embed.title = "Now Playing"
        fields = [
            ("Source", "**SoundCloud**", True),
            ("Title", f"**{track}**", True),
            ("Author", f"**{track.author}**", True),
        ]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        return await ctx.send(embed=embed)

    @commands.command(
        name="leave",
        aliases=["disconnect", "bye"],
        brief="Leave the current voice channel",
        description="Leave the current voice channel if applicable",
    )
    @commands.has_permissions(manage_guild=True)
    async def leave(self, ctx: commands.Context) -> discord.Message:

        if not await db.dj.check_dj_perms(ctx, ctx.author):
            return await ctx.send(f"You are missing DJ permissions for **{ctx.guild.name}**")
        if not ctx.voice_client:
            return await ctx.send("I am not connected to a voice channel")
        vc: wavelink.Player = ctx.voice_client
        if vc and vc.is_playing():
            vc.queue.clear()
            await vc.stop()
        await ctx.send(f"Leaving voice channel {vc.channel}")
        await ctx.voice_client.disconnect()

    @commands.command(
        name="stop",
        aliases=["forcestop"],
        brief="Force stop the queue",
        description="If applicable, force stop the current playing track and clear the queue",
    )
    @commands.has_permissions(manage_guild=True)
    async def stop(self, ctx: commands.Context) -> discord.Message:

        if not await db.dj.check_dj_perms(ctx, ctx.author):
            return await ctx.send(f"You are missing DJ permissions for **{ctx.guild.name}**")
        if not ctx.voice_client:
            return await ctx.send("I am not connected to a voice channel")
        vc: wavelink.Player = ctx.voice_client
        if vc.is_playing():
            vc.queue.clear()
            await vc.stop()
            return await ctx.send(f"Stopped playing music in channel {vc.channel}")
        return await ctx.send(f"I am not playing music in channel {vc.channel}")

    @commands.command(name="skip", brief="Skip the current track", description="Skip the current track on the player")
    async def skip(self, ctx: commands.Context) -> discord.Message:

        if not await db.dj.check_dj_perms(ctx, ctx.author):
            return await ctx.send(f"You are missing DJ permissions for **{ctx.guild.name}**")

        if not ctx.voice_client:
            return await ctx.send("I am not connected to a voice channel")
        vc: wavelink.Player = ctx.voice_client
        if not vc.is_playing():
            return await ctx.send(f"I am not playing music in channel {vc.channel}")
        await ctx.send(f"Skipping track **{vc.track}**")
        await vc.stop()

    @commands.command(
        name="next", brief="Get the next track in the queue", description="Get the next track in the queue"
    )
    async def next(self, ctx: commands.Context) -> discord.Message:

        if not ctx.voice_client:
            return await ctx.send("I am not connected to a voice channel")
        vc: wavelink.Player = ctx.voice_client
        if not vc.is_playing():
            return await ctx.send(f"I am not playing music in channel {vc.channel}")
        if not vc.queue.is_empty:
            nxt = vc.queue[0]
            embed = BaseEmbed(title="Next Track", color=ctx.guild.me.color)
            fields = [
                ("Source", "**YouTube**" if isinstance(nxt, wavelink.YouTubeTrack) else "**SoundCloud**", True),
                ("Title", f"**{nxt}**", True),
                ("Author", f"**{nxt.author}**", True),
            ]
            if isinstance(nxt, wavelink.YouTubeTrack):
                embed.set_thumbnail(url=nxt.thumbnail)
            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)
            return await ctx.send(embed=embed)
        return await ctx.send(
            f"This is the only track in the queue for **{ctx.guild.name}**. Add more tracks by using the play command."
        )

    @commands.command(
        name="nowplaying",
        aliases=["np"],
        brief="Get the track that is currently playing",
        description="Get the track that is currently playing in the queue",
    )
    async def nowplaying(self, ctx: commands.Context) -> discord.Message:

        if not ctx.voice_client:
            return await ctx.send("I am not connected to a voice channel")

        vc: wavelink.Player = ctx.voice_client

        if not vc.is_playing():
            return await ctx.send(f"I am not playing music in channel {vc.channel}")

        np = vc.track

        embed = BaseEmbed(title="Now Playing", color=ctx.guild.me.color)
        if isinstance(np, wavelink.YouTubeTrack):
            embed.set_thumbnail(url=np.thumbnail)

        fields = [
            ("Source", "**YouTube**" if isinstance(np, wavelink.YouTubeTrack) else "**SoundCloud**", True),
            ("Title", f"**{np}**", True),
            ("Author", f"**{np.author}**", True),
            ("Loop", f"**{vc.loop}**", True),
        ]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        return await ctx.send(embed=embed)

    @commands.group(
        name="queue",
        aliases=["q"],
        brief="View and manage the queue for this guild",
        description="View and manage the music queue for this guild",
        invoke_without_command=True,
    )
    async def queue(self, ctx: commands.Context) -> discord.Message:

        if not ctx.voice_client:
            return await ctx.send("I am not connected to a voice channel")
        vc: wavelink.Player = ctx.voice_client
        if vc.queue.is_empty:
            return await ctx.invoke(self.nowplaying)
        embed = BaseEmbed(title=f"Queue for {ctx.guild.name}", color=ctx.guild.me.color)
        if not vc.is_playing():
            return await ctx.send(f"I am not playing music in channel {vc.channel}")
        embed.description = (
            f"Currently Playing: '{vc.track}' by '{vc.track.author}' on {'YouTube' if isinstance(vc.track, wavelink.YouTubeTrack) else 'SoundCloud'}\n\n"
            + "\n".join(
                f"{idx+1}. '{val}' by '{val.author}' on {'YouTube' if isinstance(vc.track, wavelink.YouTubeTrack) else 'SoundCloud'}"
                for idx, val in enumerate(vc.queue)
            )
            if vc.queue
            else f"Currently Playing: '{vc.track}' by '{vc.track.author}' on {'YouTube' if isinstance(vc.track, wavelink.YouTubeTrack) else 'SoundCloud'}\n\n"
        )
        if len(embed.description) > 4000:
            return await ctx.send(
                file=discord.File(
                    BytesIO(embed.description.replace("`", "'").replace("*", "").encode("utf-8")), filename="queue.txt"
                )
            )
        else:
            return await ctx.send(embed=embed)

    @queue.command(name="shuffle", brief="Shuffle the queue", description="Shuffle the queue for random assignments")
    async def shuffle(self, ctx: commands.Context) -> discord.Message:

        if not await db.dj.check_dj_perms(ctx, ctx.author):
            return await ctx.send(f"You are missing DJ permissions for **{ctx.guild.name}**")

        if not ctx.voice_client:
            return await ctx.send("I am not connected to a voice channel")

        vc: wavelink.Player = ctx.voice_client

        if vc.queue.is_empty:
            return await ctx.send(f"No songs are queued for **{ctx.guild.name}**")
        shuffle(vc.queue._queue)
        return await ctx.send(f"Queue shuffled! Do {ctx.prefix}queue to see the new queue order.")

    @queue.command(
        name="remove",
        aliases=["delete", "pop"],
        brief="Remove an item from the queue",
        description="Remove an item from the queue using its index",
    )
    async def remove(
        self,
        ctx: commands.Context,
        index: Optional[int] = commands.Option(description="The index of the item to remove", default=1),
    ) -> discord.Message:

        if not await db.dj.check_dj_perms(ctx, ctx.author):
            return await ctx.send(f"You are missing DJ permissions for **{ctx.guild.name}**")
        if not ctx.voice_client:
            return await ctx.send("I am not connected to a voice channel")
        vc: wavelink.Player = ctx.voice_client
        if vc.queue.is_empty:
            return await ctx.send(f"No songs are queued for **{ctx.guild.name}**")
        elif index not in range(1, len(vc.queue) + 1):
            if len(vc.queue) > 1:
                error_message = (
                    f"Provided index out of queue index range. Please pass a number between 1 and {len(vc.queue)}"
                )
            else:
                error_message = f"There is only one song in the queue for **{ctx.guild.name}**. To remove it, pass the number 1 to this command."
            return await ctx.send(error_message)
        track = vc.queue._queue[index - 1]
        embed = BaseEmbed(title="Track Removed from Queue", color=ctx.guild.me.color)
        fields = [
            ("Queue Index", f"**{index}**", True),
            ("Track Source", "**YouTube**" if isinstance(track, wavelink.YouTubeTrack) else "**SoundCloud**", True),
            ("Track Name", f"**{track.title}**", True),
            ("Track Name", f"**{track.author}**", True),
        ]
        if isinstance(track, wavelink.YouTubeTrack):
            embed.set_thumbnail(url=track.thumbnail)
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        vc.queue._queue.remove(track)
        return await ctx.send(embed=embed)

    @commands.command(
        name="loop", brief="Toggle repetition of the current queue", description="Toggle repeat for the current queue"
    )
    async def loop(self, ctx: commands.Context) -> discord.Message:

        if not ctx.voice_client:
            return await ctx.send("I am not connected to a voice channel")
        vc: wavelink.Player = ctx.voice_client
        if not vc.is_playing():
            return await ctx.send(f"I am not playing music in channel {vc.channel}")
        vc.loop ^= True
        if vc.loop:
            return await ctx.send(f"Loop enabled for voice channel {vc.channel}")
        else:
            return await ctx.send(f"Loop disabled for voice channel {vc.channel}")

    @commands.group(
        name="dj", brief="DJ Management Commands", description="Manage DJs in the guild", invoke_without_command=True
    )
    async def dj(self, ctx: commands.Context) -> discord.Message:

        dj_role = await db.dj.get_dj(ctx)

        if not dj_role:
            return await ctx.send(f"There is no DJ role configured for **{ctx.guild.name}**")

        return await ctx.send(f"DJ role for **{ctx.guild.name}** is `{dj_role.name}`")

    @dj.command(name="set", brief="Set DJ role for this guild", description="Set the DJ role for this guild")
    @commands.has_permissions(manage_guild=True)
    async def set_dj(
        self,
        ctx: commands.Context,
        role: discord.Role = commands.Option(description="Please pick a role to grant DJ permissions to"),
    ) -> discord.Message:

        await db.dj.set_dj(ctx, role)
        return await ctx.send(f"New DJ role for **{ctx.guild.name}** is now `{role.name}`")

    @commands.command(name="pause", brief="Pause the queue", description="Pause the player from playing the queue")
    async def pause(self, ctx: commands.Context) -> discord.Message:

        if not await db.dj.check_dj_perms(ctx, ctx.author):
            return await ctx.send(f"You are missing DJ permissions for **{ctx.guild.name}**")

        if not ctx.voice_client:
            return await ctx.send("I am not connected to a voice channel")
        vc: wavelink.Player = ctx.voice_client
        if vc._paused:
            return await ctx.send("I am already paused")
        await vc.pause()
        return await ctx.send("Paused the player")

    @commands.command(
        name="resume", brief="Resume the queue if paused", description="Pause the player from playing the queue"
    )
    async def resume(self, ctx: commands.Context) -> discord.Message:

        if not await db.dj.check_dj_perms(ctx, ctx.author):
            return await ctx.send(f"You are missing DJ permissions for **{ctx.guild.name}**")

        if not ctx.voice_client:
            return await ctx.send("I am not connected to a voice channel")
        vc: wavelink.Player = ctx.voice_client
        if not vc._paused:
            return await ctx.send("I am already playing tracks")
        await vc.resume()
        return await ctx.send("Resumed the player")

    @play_soundcloud.before_invoke
    @play_youtube.before_invoke
    async def ensure_voice(self, ctx: commands.Context) -> discord.Message | VersarePlayer:
        if not ctx.voice_client:
            if ctx.author.voice:
                vc: VersarePlayer = await ctx.author.voice.channel.connect(cls=VersarePlayer)
                return vc
            else:
                raise commands.CommandError("Must be connected to a voice channel")


def setup(bot: commands.Bot) -> None:
    if bot.config.get("lavalink"):
        bot.add_cog(Music(bot))
