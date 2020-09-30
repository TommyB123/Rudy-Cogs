from .rcrpmodelmanager import RCRPModelManager

def setup(bot):
    bot.add_cog(RCRPModelManager(bot))