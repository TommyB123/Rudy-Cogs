import discord
import aiohttp
import ciso8601
import time
from datetime import timedelta
from discord.ext import tasks
from redbot.core import commands, Config
from redbot.core.utils import menus
from redbot.core.bot import Red


class RudyCrackwatch(commands.Cog, name="Crackwatch Watcher"):
    def __init__(self, bot: Red):
        default_global = {
            "notified_games": [],
            "watched_channels": []
        }

        self.bot = bot
        self.config = Config.get_conf(self, 45599)
        self.config.register_global(**default_global)
        self.fetch_cracked_games.add_exception_type(aiohttp.ClientError)
        self.fetch_cracked_games.start()

    def cog_unload(self):
        self.fetch_cracked_games.cancel()

    @tasks.loop(seconds=60)
    async def fetch_cracked_games(self):
        data = None
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.crackwatch.com/api/games?page=0&sort_by=crack_date&is_cracked=true') as res:
                data = await res.json()

        async with self.config.notified_games() as sent_titles:
            for title in data:
                if title['_id'] not in sent_titles:
                    embed = await self.format_game_info(title)
                    channels = await self.config.watched_channels()
                    for channel_id in channels:
                        channel = self.bot.get_channel(channel_id)
                        if channel is not None:
                            await channel.send(embed=embed)
                    sent_titles.append(title['_id'])

    @fetch_cracked_games.before_loop
    async def before_fetch_cracked_games(self):
        await self.bot.wait_until_ready()

    async def format_game_info(self, game):
        protections = ', '.join(game['protections'])
        groups = ', '.join(game['groups'])
        crackdate = ciso8601.parse_datetime(game['crackDate'])
        releasedate = ciso8601.parse_datetime(game['releaseDate'])
        crackunix = time.mktime(crackdate.timetuple())
        releaseunix = time.mktime(releasedate.timetuple())
        d = timedelta(seconds=crackunix - releaseunix)
        days = d.days
        if days < 0:
            days = 1

        embed = discord.Embed(title="", url=game['url'], description=f"{game['title']} has been cracked!", color=0x00e205)
        embed.set_author(name="Crackwatch", url=game['url'], icon_url="https://crackwatch.com/icons/crackwatch.png")
        embed.set_thumbnail(url=game['imagePoster'])
        embed.add_field(name="Release Date", value=releasedate.date().isoformat(), inline=True)
        embed.add_field(name="Crack Date", value=crackdate.date().isoformat(), inline=True)
        embed.add_field(name="Time Taken", value=f'{days} {"day" if days == 1 else "days"}', inline=True)
        embed.add_field(name="DRM", value=protections, inline=True)
        embed.add_field(name="Group", value=groups, inline=True)
        return embed

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        async with self.config.watched_channels() as channels:
            if channel.id in channels:
                channels.remove(channel.id)

    @commands.group()
    async def crackwatch(self, ctx: commands.Context):
        """Various commands that interact with crackwatch."""
        pass

    @crackwatch.command()
    @commands.mod_or_permissions(manage_guild=True)
    async def setalertchannel(self, ctx: commands.Context, channel: discord.TextChannel = None):
        """Assigns a channel that will receive notifications whenever a new game is marked as cracked on Crackwatch.
        If you'd like to unassign a channel, run this command in the channel that's already been set."""
        async with self.config.watched_channels() as channels:
            if channel is None:
                if channel.id not in channels:
                    await ctx.send('Specify a channel to link Crackwatch notifications to.')
                else:
                    channels.remove(channel.id)
                    await ctx.send('This channel will no longer receive Crackwatch notifications.')  # using ctx to send here because channel and ctx.channel would be identical
            else:
                if channel.id in channels:
                    await ctx.send(f'{channel.mention} already receives Crackwatch notifications.')
                else:
                    channels.append(channel.id)
                    await channel.send('This channel will now receive Crackwatch notifications.')
                    await ctx.send(f'{channel.mention} will now receive Crackwatch notifications.')

    @crackwatch.command()
    async def recent(self, ctx: commands.Context):
        """Fetches the 30 most recently cracked games."""
        data = None
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('https://api.crackwatch.com/api/games?page=0&sort_by=crack_date&is_cracked=true') as res:
                    data = await res.json()
        except aiohttp.ClientError:
            await ctx.send('Failed to fetch data from Crackwatch API. The website is likely experiencing high load and/or is down.')
            return

        embeds = []
        for game in data:
            embed = await self.format_game_info(game)
            embeds.append(embed)

        await menus.menu(ctx, embeds, menus.DEFAULT_CONTROLS)
