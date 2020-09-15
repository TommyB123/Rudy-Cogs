import discord
import random
from imgurpython import ImgurClient
from redbot.core import commands
from .utility import rudyfriend, rcrpguildid, rudy_check, management_check

#imgur client handler
imclient = ImgurClient('6f85cfd1f822e7b', '629f840ae2bf44b669560b64403c3f8511293777')

async def isrudyfriend(ctx: commands.Context):
    if ctx.guild.id == rcrpguildid:
        if rudyfriend in [role.id for role in ctx.author.roles]:
            return True
        else:
            return False
    else:
        return True

async def SendRandomAlbumPicture(ctx: commands.Context, album: str):
    async with ctx.typing():
        pictures = []
        for image in imclient.get_album_images(album):
            pictures.append(image.link)
        await ctx.send(random.choice(pictures))

class RudyPic(commands.Cog, name = "rudypic"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.check(rudy_check)
    @commands.check(isrudyfriend)
    async def rudypic(self, ctx: commands.Context):
        """Sends an adorable picture of Rudy"""
        await SendRandomAlbumPicture(ctx, 'WLQku0l')

    @commands.command()
    @commands.guild_only()
    @commands.check(rudy_check)
    @commands.check(isrudyfriend)
    async def sammypic(self, ctx: commands.Context):
        """Sends an adorable picture of Sammy"""
        await SendRandomAlbumPicture(ctx, 'VfKwj4H')

    @commands.command()
    @commands.guild_only()
    @commands.check(rudy_check)
    @commands.check(isrudyfriend)
    async def milopic(self, ctx: commands.Context):
        """Sends an adorable picture of Milo"""
        await SendRandomAlbumPicture(ctx, 'h3VORpQ')

    @commands.command()
    @commands.guild_only()
    @commands.check(management_check)
    async def gizmo(self, ctx: commands.Context):
        """Sends a legendary Gizmo quote"""
        await SendRandomAlbumPicture(ctx, 'SlgjJJu')

    @commands.command()
    @commands.guild_only()
    @commands.check(management_check)
    async def lylat(self, ctx: commands.Context):
        """Sends a legendary Lylat quote"""
        await SendRandomAlbumPicture(ctx, 'LF00KOm')
