from .rcrpapplications import RCRPApplications


async def setup(bot):
    await bot.add_cog(RCRPApplications(bot))
