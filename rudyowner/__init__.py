from .rudyowner import OwnerCog


async def setup(bot):
    await bot.add_cog(OwnerCog())
