from .rudylogging import RudyLogging


async def setup(bot):
    await bot.add_cog(RudyLogging(bot))
