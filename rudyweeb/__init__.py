from .rudyweeb import WeebCommands


async def setup(bot):
    await bot.add_cog(WeebCommands(bot))
