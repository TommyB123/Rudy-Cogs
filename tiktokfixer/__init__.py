from .tiktokfixer import TiktokFixer


async def setup(bot):
    await bot.add_cog(TiktokFixer(bot))
