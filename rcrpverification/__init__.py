from .rcrpverification import RCRPVerification


async def setup(bot):
    await bot.add_cog(RCRPVerification(bot))
