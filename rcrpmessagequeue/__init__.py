from .rcrpmessagequeue import RCRPMessageQueue

def setup(bot):
    bot.add_cog(RCRPMessageQueue(bot))