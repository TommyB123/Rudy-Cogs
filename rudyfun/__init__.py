from .rudyfun import FunCommands


async def setup(bot):
    await bot.add_cog(FunCommands())
