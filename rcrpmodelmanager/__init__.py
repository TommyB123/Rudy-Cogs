from .rcrpmodelmanager import RCRPModelManager


async def setup(bot):
    await bot.add_cog(RCRPModelManager(bot))
