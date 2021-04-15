from .rcrpapplications import RCRPApplications


def setup(bot):
    bot.add_cog(RCRPApplications(bot))
