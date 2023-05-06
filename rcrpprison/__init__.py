from .rcrpprison import RCRPPrison


async def setup(bot):
    await bot.add_cog(RCRPPrison(bot))
