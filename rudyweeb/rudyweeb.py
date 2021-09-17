import discord
import aiohttp
import json
import random
from redbot.core import commands, Config
from redbot.core.utils.chat_formatting import humanize_list

degenerate_categories = [
    'femdom', 'tickle', 'classic', 'ngif', 'erofeet', 'erok', 'poke', 'les', 'v3', 'hololewd', 'lewdk', 'keta',
    'feetg', 'nsfw_neko_gif', 'eroyuri', 'kiss', '8ball', 'kuni', 'tits', 'pussy_jpg', 'cum_jpg', 'pussy', 'lewdkemo',
    'slap', 'lewd', 'cum', 'cuddle', 'spank', 'smallboobs', 'Random_hentai_gif', 'avatar', 'fox_girl', 'nsfw_avatar',
    'hug', 'gecg', 'boobs', 'pat', 'feet', 'smug', 'kemonomimi', 'solog', 'holo', 'wallpaper', 'bj', 'yuri', 'anal',
    'baka', 'blowjob', 'holoero', 'feed', 'neko', 'gasm', 'hentai', 'futanari', 'ero', 'solo', 'waifu', 'pwankg', 'eron', 'erokemo'
]


async def fetchweeb(session: aiohttp.ClientSession, url: str):
    async with session.get(url) as response:
        return await response.text()

async def sendweeb(url: str):
    async with session.get(url) as response:
        return await response.text()


async def isweeb(ctx: commands.Context):
    weeb = WeebCommands(commands.Cog)
    weeb.config = Config.get_conf(weeb, identifier=45599)

    async with weeb.config.weebs() as weebs:
        if ctx.author.id in weebs:
            return True

    if ctx.guild is not None:
        async with weeb.config.weebservers() as weebservers:
            if ctx.guild.id in weebservers:
                return True

    return False


class WeebCommands(commands.Cog, name="Weeb"):
    def __init__(self, bot):
        default_global = {
            "weebs": [],
            "weebservers": []
        }

        self.bot = bot
        self.config = Config.get_conf(self, identifier=45599)
        self.config.register_global(**default_global)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        async with self.config.weebservers() as guild_ids:
            if guild.id in guild_ids:
                guild_ids.remove(guild.id)

    @commands.command()
    @commands.guild_only()
    @commands.check(isweeb)
    async def weeb(self, ctx: commands.Context):
        """Bad"""
        async with aiohttp.ClientSession() as session:
            response = await fetchweeb(session, 'https://nekos.life/api/v2/img/neko')
            image = json.loads(response)
            await ctx.send(image['url'])

    @commands.command()
    @commands.guild_only()
    @commands.is_nsfw()
    @commands.check(isweeb)
    async def lewdweeb(self, ctx: commands.Context):
        """Really bad"""
        async with aiohttp.ClientSession() as session:
            response = await fetchweeb(session, 'https://nekos.life/api/v2/img/lewd')
            image = json.loads(response)
            await ctx.send(image['url'])

    @commands.command()
    @commands.guild_only()
    @commands.is_nsfw()
    @commands.check(isweeb)
    async def degenerate(self, ctx: commands.Context, *, category: str = ""):
        """The worst"""
        if category == '*':
            category = random.choice(degenerate_categories)

        if category not in degenerate_categories:
            cats = humanize_list(degenerate_categories)
            await ctx.send(f"Not a valid degenerate category. '*' can be used to grab a random category. Valid categories: {cats}")
            return

        async with aiohttp.ClientSession() as session:
            response = await fetchweeb(session, f'https://nekos.life/api/v2/img/{category}')
            image = json.loads(response)
            await ctx.send(image['url'])

    @commands.command()
    @commands.guild_only()
    async def lizard(self, ctx: commands.Context):
        """Delivers a lizard to your front door"""
        async with aiohttp.ClientSession() as session:
            response = await fetchweeb(session, 'https://nekos.life/api/v2/img/lizard')
            image = json.loads(response)
            await ctx.send(image['url'])

    @commands.command()
    @commands.guild_only()
    async def woof(self, ctx: commands.Context):
        """Puts a nice pup out on display"""
        async with aiohttp.ClientSession() as session:
            response = await fetchweeb(session, 'https://nekos.life/api/v2/img/woof')
            image = json.loads(response)
            await ctx.send(image['url'])

    @commands.command()
    @commands.guild_only()
    async def meow(self, ctx: commands.Context):
        """Puts a nice cat out on display"""
        async with aiohttp.ClientSession() as session:
            response = await fetchweeb(session, 'https://nekos.life/api/v2/img/meow')
            image = json.loads(response)
            await ctx.send(image['url'])

    @commands.command()
    @commands.guild_only()
    async def goose(self, ctx: commands.Context):
        """goose"""
        async with aiohttp.ClientSession() as session:
            response = await fetchweeb(session, 'https://nekos.life/api/v2/img/goose')
            image = json.loads(response)
            await ctx.send(image['url'])

    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def makeweeb(self, ctx: commands.Context, target: discord.Member):
        """Certifies or banishes a dude from the weebs"""
        async with self.config.weebs() as weebs:
            if target.id in weebs:
                weebs.remove(target.id)
                await ctx.send(f'{target.mention} has been banished from the weebs.')
            else:
                weebs.append(target.id)
                await ctx.send(f'{target.mention} is now a certified weeb!')

    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def makeserverweeb(self, ctx: commands.Context):
        """Certifies or banishes a server from the weebs"""
        async with self.config.weebservers() as weebservers:
            if ctx.guild.id in weebservers:
                weebservers.remove(ctx.guild.id)
                await ctx.send(f'Server **{ctx.guild.name}** has been banished from the weebs.')
            else:
                weebservers.append(ctx.guild.id)
                await ctx.send(f'**{ctx.guild.name}** is now a certified weeb server!')
