from .rudycrackwatch import RudyCrackwatch


async def setup(bot):
    await bot.add_cog(RudyCrackwatch(bot))
