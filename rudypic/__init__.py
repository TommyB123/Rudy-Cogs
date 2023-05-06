from .rudypic import RudyPic


async def setup(bot):
    await bot.add_cog(RudyPic(bot))
