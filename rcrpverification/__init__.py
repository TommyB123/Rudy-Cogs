from .rcrpverification import RCRPVerification


def setup(bot):
    bot.add_cog(RCRPVerification(bot))
