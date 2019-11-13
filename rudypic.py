import discord
import utility

from imgurpython import ImgurClient
from discord import commands

#imgur client handler
imclient = ImgurClient('6f85cfd1f822e7b', '629f840ae2bf44b669560b64403c3f8511293777')

class RudypicCog(commands.Cog, name="rudypic"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help = "Sends an adorable picture of Rudy")
    async def rudypic(self, ctx):
        if rudyfriend in [role.id for role in ctx.author.roles]:
            pictures = []
            for image in imclient.get_album_images('WLQku0l'):
                pictures.append(image.link)
            await ctx.send(random.choice(pictures))
        else:
            await ctx.message.delete()

def setup(bot):
    bot.add_cog(RudypicCog(bot))