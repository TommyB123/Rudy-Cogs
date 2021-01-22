from .rcrprolesync import RCRPRoleSync


def setup(bot):
    bot.add_cog(RCRPRoleSync(bot))
