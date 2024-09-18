from .redditfixer import RedditFixer


async def setup(bot):
    await bot.add_cog(RedditFixer(bot))
