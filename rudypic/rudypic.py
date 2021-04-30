import discord
import random
from imgurpython import ImgurClient
from redbot.core import commands, Config

# imgur client handler
imclient = ImgurClient('6f85cfd1f822e7b', '629f840ae2bf44b669560b64403c3f8511293777')


async def isrudyfriend(ctx: commands.Context):
    rudy = RudyPic(commands.Cog)
    rudy.config = Config.get_conf(rudy, identifier=45599)
    rudyfriends = await rudy.config.rudy_friends()
    return ctx.author.id in rudyfriends


class RudyPic(commands.Cog, name="rudypic"):
    def __init__(self, bot):
        self.bot = bot
        default_global = {
            "rudy_friends": []
        }

        self.config = Config.get_conf(self, identifier=45599)
        self.config.register_global(**default_global)

    async def send_album_picture(self, ctx: commands.Context, album: str):
        try:
            final_url = None
            async with ctx.typing():
                pictures = []
                for image in imclient.get_album_images(album):
                    pictures.append(image.link)
                final_url = random.choice(pictures)
            await ctx.send(final_url)
        except Exception:
            await ctx.send('Failed to fetch album photo. Imgur API is probably down because it sucks.')

    @commands.command()
    @commands.guild_only()
    @commands.check(isrudyfriend)
    async def rudypic(self, ctx: commands.Context):
        """Sends an adorable picture of Rudy"""
        await self.send_album_picture(ctx, 'WLQku0l')

    @commands.command()
    @commands.guild_only()
    @commands.check(isrudyfriend)
    async def sammypic(self, ctx: commands.Context):
        """Sends an adorable picture of Sammy"""
        await self.send_album_picture(ctx, 'VfKwj4H')

    @commands.command()
    @commands.guild_only()
    @commands.check(isrudyfriend)
    async def milopic(self, ctx: commands.Context):
        """Sends an adorable picture of Milo"""
        await self.send_album_picture(ctx, 'h3VORpQ')

    @commands.command()
    @commands.guild_only()
    async def gizmo(self, ctx: commands.Context):
        """Sends a legendary Gizmo quote"""
        await self.send_album_picture(ctx, 'SlgjJJu')

    @commands.command()
    @commands.guild_only()
    async def lylat(self, ctx: commands.Context):
        """Sends a legendary Lylat quote"""
        await self.send_album_picture(ctx, 'LF00KOm')

    @commands.command()
    @commands.guild_only()
    async def frog(self, ctx: commands.Context):
        """Sends a nice frog"""
        await self.send_album_picture(ctx, 'yIW3G5g')

    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def rudyfriend(self, ctx: commands.Context, target: discord.Member):
        async with self.config.rudy_friends() as rudyfriends:
            if target.id in rudyfriends:
                rudyfriends.remove(target.id)
                await ctx.send(f'{target.mention} is no longer a Rudy friend!')
            else:
                rudyfriends.append(target.id)
                await ctx.send(f'{target.mention} is now a Rudy friend!')
