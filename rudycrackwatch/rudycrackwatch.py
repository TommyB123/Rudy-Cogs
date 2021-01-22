import discord
import asyncio
import aiohttp
import ciso8601
import time
from datetime import timedelta
from redbot.core import commands, Config
from redbot.core.utils import menus


class RudyCrackwatch(commands.Cog, name="Crackwatch Watcher"):
    def __init__(self, bot: discord.Client):
        default_global = {
            "last_cracked_game": None
        }

        default_guild = {
            "watch_channel": None
        }

        self.bot = bot
        self.config = Config.get_conf(self, 45599)
        self.config.register_guild(**default_guild)
        self.config.register_global(**default_global)
        self.game_check_task = self.bot.loop.create_task(self.fetch_cracked_games())

    async def fetch_cracked_games(self):
        while 1:
            data = None
            async with aiohttp.ClientSession() as session:
                async with session.get('https://api.crackwatch.com/api/games?page=0&sort_by=crack_date&is_cracked=true') as res:
                    data = await res.json()

            last_title = await self.config.last_cracked_game()
            if last_title != data[0]['title']:
                embed = await self.format_game_info(data)
                for guild in self.bot.guilds:
                    channel_id = await self.config.guild(guild).watch_channel()
                    if channel_id in [channel.id for channel in guild.channels]:
                        channel = await self.bot.get_channel(channel_id)
                        if channel is not None:
                            await channel.send(embed=embed)
            last_title = data[0]['title']
            await self.config.last_cracked_game.set(last_title)
            await asyncio.sleep(60)

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
        if channel.id == await self.config.guild(channel.guild).watch_channel():
            await self.config.guild(channel.guild).watch_channel.set(None)

    @commands.group()
    async def crackwatch(self, ctx: commands.Context):
        """Various commands that interact with crackwatch."""
        pass

    @crackwatch.command()
    @commands.mod_or_permissions(manage_guild=True)
    async def setalertchannel(self, ctx: commands.Context, channel: discord.TextChannel = None):
        """Assigns a channel that will receive notifications whenever a new game is marked as cracked on Crackwatch."""
        if channel is None:
            if await self.config.guild(ctx.guild).watch_channel is None:
                await ctx.send('Specify a channel to link Crackwatch notifications to.')
            else:
                channel_id = await self.config.guild(ctx.guild).watch_channel()
                channel = self.bot.get_channel(channel_id)
                await self.config.guild(ctx.guild).watch_channel.set(None)
                await ctx.send('This guild will no longer receive Crackwatch notifications.')
        else:
            await self.config.guild(ctx.guild).watch_channel.set(channel.id)
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

    def cog_unload(self):
        self.game_check_task.cancel()
