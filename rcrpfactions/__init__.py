from .rcrpfactions import RCRPFactions


async def setup(bot):
    await bot.add_cog(RCRPFactions(bot))
