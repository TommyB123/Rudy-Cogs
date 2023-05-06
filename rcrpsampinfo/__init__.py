from .rcrpsampinfo import RCRPSampInfo


async def setup(bot):
    await bot.add_cog(RCRPSampInfo(bot))
