import discord
from discord.ext import commands

class OwnerCmdsCog(commands.Cog, name="Owner Commands"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden = True)
    @commands.is_owner()
    async def dms(self, ctx):
        await ctx.send("<https://imgur.com/a/yYK5dnZ>")

def setup(bot):
    bot.add_cog(OwnerCmdsCog(bot))