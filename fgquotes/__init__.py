from .fgquotes import FGQuotes


def setup(bot):
    bot.add_cog(FGQuotes(bot))
