from .webmfixer import WebMFixer


async def setup(bot):
    await bot.add_cog(WebMFixer(bot))
