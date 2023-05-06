from .fgquotes import FGQuotes


async def setup(bot):
    await bot.add_cog(FGQuotes(bot))
