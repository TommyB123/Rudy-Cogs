from .instagramfixer import InstagramFixer


async def setup(bot):
    await bot.add_cog(InstagramFixer(bot))
