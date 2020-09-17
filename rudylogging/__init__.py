from .rudylogging import RudyLogging

def setup(bot):
    bot.add_cog(RudyLogging(bot))
