import discord
import aiohttp
import json
import redbot
from redbot.core import commands, Config

degenerate_categories = [
    'femdom', 'tickle', 'classic', 'ngif', 'erofeet', 'meow', 'erok', 'poke', 'les', 'v3', 'hololewd', 'lewdk', 'keta',
    'feetg', 'nsfw_neko_gif', 'eroyuri', 'kiss', '8ball', 'kuni', 'tits', 'pussy_jpg', 'cum_jpg', 'pussy', 'lewdkemo',
    'lizard', 'slap', 'lewd', 'cum', 'cuddle', 'spank', 'smallboobs', 'goose', 'random_hentai_gif', 'avatar', 'fox_girl',
    'nsfw_avatar', 'hug', 'gecg', 'boobs', 'pat', 'feet', 'smug', 'kemonomimi', 'solog', 'holo', 'wallpaper', 'bj', 'woof',
    'yuri', 'trap', 'anal', 'baka', 'blowjob', 'holoero', 'feed', 'neko', 'gasm', 'hentai', 'futanari', 'ero', 'solo', 'waifu',
    'pwankg', 'eron', 'erokemo'
]

async def fetchweeb(session, url):
    async with session.get(url) as response:
        return await response.text()

async def isweeb(ctx):
    weeb = WeebCommands(commands.Cog)
    weeb.config = Config.get_conf(weeb, identifier=45599)
    weebs = await weeb.config.weebs()
    return ctx.author.id in weebs

class WeebCommands(commands.Cog, name = "Weeb"):
    def __init__(self, bot):
        default_global = {
            "weebs": []
        }

        self.bot = bot
        self.config = Config.get_conf(self, identifier=45599)
        self.config.register_global(**default_global)

    @commands.command(help = "Bad")
    @commands.guild_only()
    @commands.check(isweeb)
    async def weeb(self, ctx):
        async with aiohttp.ClientSession() as session:
            response = await fetchweeb(session, 'https://nekos.life/api/v2/img/neko')
            image = json.loads(response)
            await ctx.send(image['url'])

    @commands.command(help = "Really bad")
    @commands.guild_only()
    @commands.is_nsfw()
    @commands.check(isweeb)
    async def lewdweeb(self, ctx):
        async with aiohttp.ClientSession() as session:
            response = await fetchweeb(session, 'https://nekos.life/api/v2/img/lewd')
            image = json.loads(response)
            await ctx.send(image['url'])

    @commands.command(help = "The worst")
    @commands.guild_only()
    @commands.is_nsfw()
    @commands.check(isweeb)
    async def degenerate(self, ctx, *, category: str = ""):
        if category not in degenerate_categories:
            await ctx.send(f"Not a valid degenerate category. Valid categories: {degenerate_categories}")
            return

        async with aiohttp.ClientSession() as session:
            response = await fetchweeb(session, f'https://nekos.life/api/v2/img/{category}')
            image = json.loads(response)
            await ctx.send(image['url'])

    @commands.command(help = "Bad (old)")
    @commands.guild_only()
    @commands.cooldown(1, 60)
    @commands.check(isweeb)
    async def oldweeb(self, ctx):
        async with aiohttp.ClientSession() as session:
            response = await fetchweeb(session, 'https://neko-love.xyz/api/v1/neko')
            image = json.loads(response)
            await ctx.send(image['url'])

    @commands.command(help = "Really bad (old)")
    @commands.guild_only()
    @commands.is_nsfw()
    @commands.check(isweeb)
    async def oldlewdweeb(self, ctx):
            async with aiohttp.ClientSession() as session:
                response = await fetchweeb(session, 'https://neko-love.xyz/api/v1/nekolewd')
                image = json.loads(response)
                await ctx.send(image['url'])
    
    @commands.command(help = "Register a dude as a weeb :)")
    @commands.guild_only()
    @commands.is_owner()
    async def registerweeb(self, ctx, member: discord.Member):
        weebs = await self.config.weebs()
        if member.id in weebs:
            await ctx.send("This member is already a weeb.")
            return
        
        weebs.append(member.id)
        await self.config.weebs.set(weebs)
        await ctx.send(f'{member.mention} is now a certified weeb!')
    
    @commands.command(help = "Banishes a weeb")
    @commands.guild_only()
    @commands.is_owner()
    async def banishweeb(self, ctx, member: discord.Member):
        weebs = await self.config.weebs()
        if member.id not in weebs:
            await ctx.send("This member is not a weeb.")
            return

        weebs.remove(member.id)
        await self.config.weebs.set(weebs)
        await ctx.send(f'{member.mention} has been banished from the weebs.')
