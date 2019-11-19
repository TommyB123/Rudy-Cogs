import discord
import random
from imgurpython import ImgurClient
from discord.ext import commands
from cogs.utility import *

#imgur client handler
imclient = ImgurClient('6f85cfd1f822e7b', '629f840ae2bf44b669560b64403c3f8511293777')

async def isrudyfriend(ctx):
    if rudyfriend in [role.id for role in ctx.author.roles]:
        return True
    else:
        return False

class RudypicCog(commands.Cog, name="rudypic"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help = "Sends an adorable picture of Rudy")
    @commands.guild_only()
    @commands.check(isrudyfriend)
    async def rudypic(self, ctx):
        pictures = []
        for image in imclient.get_album_images('WLQku0l'):
            pictures.append(image.link)
        await ctx.send(random.choice(pictures))

    @commands.command(help = "Sends an adorable picture of Sammy")
    @commands.guild_only()
    @commands.check(isrudyfriend)
    async def sammypic(self, ctx):
        pictures = []
        for image in imclient.get_album_images('WLCguFk'):
            pictures.append(image.link)
        await ctx.send(random.choice(pictures))

def setup(bot):
    bot.add_cog(RudypicCog(bot))