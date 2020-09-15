import discord
import aiomysql
from random import randint
from redbot.core import commands
from .config import mysqlconfig
from .utility import rcrp_check, management_check, member_is_verified, dashboardurl, rcrpguildid, testerrole, adminrole, helperrole, verifiedrole, managementrole

async def account_accepted(mastername: str):
    sql = await aiomysql.connect(**mysqlconfig)
    cursor = await sql.cursor()
    await cursor.execute("SELECT NULL FROM masters WHERE Username = %s AND State = 1", (mastername, ))
    data = await cursor.fetchone()
    await cursor.close()
    sql.close()

    if data is None:
        return False
    else:
        return True

async def account_verified(name: str):
    sql = await aiomysql.connect(**mysqlconfig)
    cursor = await sql.cursor()
    await cursor.execute("SELECT NULL FROM masters WHERE Username = %s AND discordid != 0", (name, ))
    data = await cursor.fetchone()
    await cursor.close()
    sql.close()

    if data is None:
        return False
    else:
        return True
    
async def account_name_valid(name: str):
    sql = await aiomysql.connect(**mysqlconfig)
    cursor = await sql.cursor()
    await cursor.execute("SELECT NULL FROM masters WHERE Username = %s", (name, ))
    data = await cursor.fetchone()
    await cursor.close()
    sql.close()

    if data is None:
        return False
    else:
        return True

async def account_linked_to_discord(discordid: int):
    sql = await aiomysql.connect(**mysqlconfig)
    cursor = await sql.cursor()
    await cursor.execute("SELECT NULL FROM masters WHERE discordid = %s", (discordid, ))
    data = await cursor.fetchone()
    await cursor.close()
    sql.close()

    if data is None:
        return False
    else:
        return True

def random_with_N_digits(n: int):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

class RCRPVerification(commands.Cog, name="RCRP Verification"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.dm_only()
    async def verify(self, ctx: commands.Context, masteraccount: str):
        """Verifies ownership between a Discord and RCRP account"""
        if masteraccount == None:
            await ctx.send("Usage: !verify [Master Account Name]")
            return

        if await account_linked_to_discord(ctx.author.id) == True:
            await ctx.send("This Discord account is already linked to an RCRP account.")
            return

        if await account_name_valid(masteraccount) == False:
            await ctx.send("Invalid account name.")
            return

        if await account_accepted(masteraccount) == False:
            await ctx.send("You cannot verify your Master Account if you have not been accepted into the server.\nIf you're looking for help with the registration process, visit our forums at https://forum.redcountyrp.com")
            return

        if await account_verified(masteraccount) == True:
            await ctx.send("This master account has already been verified before. If you are trying to verify a new discord account, please create a support ticket at https://redcountyrp.com/user/tickets.")
            return

        code = random_with_N_digits(10)
        sql = await aiomysql.connect(**mysqlconfig)
        cursor = await sql.cursor()
        await cursor.execute("UPDATE masters SET discordcode = %s, pendingdiscordid = %s WHERE Username = %s AND discordid = 0", (str(code), ctx.author.id, masteraccount))
        await cursor.close()
        sql.close()

        await ctx.send(f"Your verification code has been set! Log in on our website and look for 'Discord Verification Code' at your dashboard page. ({dashboardurl})\nOnce you have found your verification code, send '!validate [code]' to confirm your account.")

    @commands.command()
    @commands.dm_only()
    async def validate(self, ctx, code: int):
        """Validates the verification code set to an RCRP account"""
        sql = await aiomysql.connect(**mysqlconfig)
        cursor = await sql.cursor(aiomysql.DictCursor)
        await cursor.execute("SELECT COUNT(*) AS matches, id, Helper, Tester, AdminLevel FROM masters WHERE discordcode = %s AND pendingdiscordid = %s", (code, ctx.author.id))
        data = await cursor.fetchone()

        if data['matches'] == 0: #account doesn't match
            await ctx.send("Invalid verification code.")
            return

        rcrpguild = self.bot.get_guild(rcrpguildid)
        discordmember = rcrpguild.get_member(ctx.author.id)
        discordroles = []
        discordroles.append(rcrpguild.get_role(verifiedrole))
        if data['Helper'] == 1: #guy is helper
            discordroles.append(rcrpguild.get_role(helperrole))
        if data['Tester'] == 1: #guy is tester
            discordroles.append(rcrpguild.get_role(testerrole))
        if data['AdminLevel'] != 0: #guy is admin
            discordroles.append(rcrpguild.get_role(adminrole))
        if data['AdminLevel'] == 4: #guy is management
            discordroles.append(rcrpguild.get_role(managementrole))
        await discordmember.add_roles(*discordroles)

        await cursor.execute("UPDATE masters SET discordid = %s, discordcode = 0, pendingdiscordid = 0 WHERE id = %s", (ctx.author.id, data['id']))
        await cursor.close()
        sql.close()

        await ctx.send("Your account is now verified!")

    @commands.command()
    @commands.guild_only()
    @commands.check(rcrp_check)
    @commands.check(management_check)
    async def manualverify(self, ctx: commands.Context, member: discord.Member, masteraccount: str):
        """Manually link a discord account to an RCRP account"""
        if member_is_verified(member) == True:
            await ctx.send(f"{member.mention} is already verified.")
            return

        if await account_name_valid(masteraccount) == False:
            await ctx.send("Invalid MA name")
            return

        if await account_verified(masteraccount) == True:
            await ctx.send("MA is already verified")
            return

        sql = await aiomysql.connect(**mysqlconfig)
        cursor = await sql.cursor()
        await cursor.execute("UPDATE masters SET discordid = %s, discordcode = 0 WHERE Username = %s", (member.id, masteraccount))
        await cursor.close()
        sql.close()

        await member.add_roles(ctx.guild.get_role(verifiedrole))
        await ctx.send(f"{member.mention} has been manually verified as {masteraccount}")

    @commands.command()
    @commands.guild_only()
    @commands.check(rcrp_check)
    @commands.check(management_check)
    async def unverify(self, ctx: commands.Context, member: discord.Member):
        """Remove a discord account's verification status and unlinks their RCRP account."""
        if member_is_verified(member) == False:
            await ctx.send("This user is not verified")
            return

        sql = await aiomysql.connect(**mysqlconfig)
        cursor = await sql.cursor()
        await cursor.execute("DELETE FROM discordroles WHERE discorduser = %s", (member.id, ))
        await cursor.execute("UPDATE masters SET discordid = 0 WHERE discordid = %s", (member.id, ))
        await cursor.close()
        sql.close()

        await member.remove_roles(*member.roles)
        await ctx.send(f"{member.mention} has been unverified.")

    @commands.command()
    @commands.guild_only()
    @commands.check(rcrp_check)
    @commands.check(management_check)
    async def softunverify(self, ctx: commands.Context, discordid: int):
        """Unlinks an RCRP account from a Discord ID. Useful for when a Discord account no longer exists or is no longer used by its owner"""
        sql = await aiomysql.connect(**mysqlconfig)
        cursor = await sql.cursor()
        await cursor.execute("UPDATE masters SET discordid = 0 WHERE discordid = %s", (discordid))

        if cursor.rowcount != 0:
            await ctx.send(f"Discord ID {discordid} has been unlinked from its MA.")
        else:
            await ctx.send(f"There are no accounts linked to Discord ID {discordid}")

        await cursor.close()
        sql.close()
