import discord
import aiomysql
from redbot.core import commands
from redbot.core.bot import Red

# guild id for the prison guild
prisonguildid = 558036120743706625


async def prison_check(ctx: commands.Context):
    return ctx.guild is not None and ctx.guild.id == prisonguildid


class RCRPPrison(commands.Cog, name="RCRP Prison"):
    def __init__(self, bot: Red):
        self.bot = bot

    @commands.group()
    @commands.guild_only()
    @commands.check(prison_check)
    async def prison(self, ctx: commands.Context):
        """Various prison-related commands"""
        pass

    @prison.command()
    @commands.guild_only()
    @commands.check(prison_check)
    async def inmates(self, ctx: commands.Context):
        """Fetches a list of inmates that are currently in-game"""
        mysqlconfig = await self.bot.get_shared_api_tokens('mysql')
        sql = await aiomysql.connect(**mysqlconfig)
        cursor = await sql.cursor()

        await cursor.execute("SELECT players.Name, masters.Username, settingval, extra1 FROM psettings LEFT JOIN players ON psettings.sqlid = players.id LEFT JOIN masters ON players.MasterAccount = masters.id WHERE setting = 6 AND players.Online = 1")
        if cursor.rowcount == 0:
            await cursor.close()
            sql.close()
            await ctx.send('There are currently no online prisoners.')
            return

        prisoners = await cursor.fetchall()
        prisonstring = []
        for prisoner in prisoners:
            minutes = "minutes" if cursor.rowcount != 1 else "minute"
            prisonstring.append(f'{prisoner[0]} ({prisoner[1]}) - Cell {prisoner[3]} ({prisoner[2]} {minutes} remaining)')
        prisonstring = '\n'.join(prisonstring)
        prisonstring = prisonstring.replace('_', ' ')

        embed = discord.Embed(title=f'Online Prisoners ({cursor.rowcount})', description=prisonstring, color=0xe74c3c)
        embed.timestamp = ctx.message.created_at
        await ctx.send(embed=embed)

        await cursor.close()
        sql.close()

    @prison.command()
    @commands.guild_only()
    @commands.check(prison_check)
    async def guards(self, ctx: commands.Context):
        """Fetches a list of guards that are currently in-game"""
        await ctx.send("wip")
