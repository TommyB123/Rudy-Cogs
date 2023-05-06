from .rcrprolesync import RCRPRoleSync


async def setup(bot):
    await bot.add_cog(RCRPRoleSync(bot))
