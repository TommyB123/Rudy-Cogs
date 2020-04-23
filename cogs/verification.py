import discord
import aiomysql
from discord.ext import commands
from utility import rcrp_check, management_check, random_with_N_digits, account_name_valid, member_is_verified, account_linked_to_discord, account_accepted, account_verified, dashboardurl, rcrpguildid, testerrole, adminrole, helperrole, verifiedrole, managementrole, mysql_connect

class VerificationCog(commands.Cog, name="RCRP Verification"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.dm_only()
    async def verify(self, ctx, masteraccount:str = None):
        if masteraccount is None:
            await ctx.send("Usage: !verify [Master account name]")
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
        sql = await mysql_connect()
        cursor = await sql.cursor()
        await cursor.execute("UPDATE masters SET discordcode = %s, pendingdiscordid = %s WHERE Username = %s AND discordid = 0", (str(code), ctx.author.id, masteraccount))
        await cursor.close()
        sql.close()

        await ctx.send(f"Your verification code has been set! Log in on our website and look for 'Discord Verification Code' at your dashboard page. ({dashboardurl})\nOnce you have found your verification code, send '!validate [code]' to confirm your account.")

    @commands.command()
    @commands.dm_only()
    async def validate(self, ctx, code:int = None):
        if code == None:
            await ctx.send("Usage: !validate [code]")

        sql = await mysql_connect()
        cursor = await sql.cursor(aiomysql.DictCursor)
        await cursor.execute("SELECT COUNT(*) AS matches, id, Helper, Tester, AdminLevel FROM masters WHERE discordcode = %s AND pendingdiscordid = %s", (code, ctx.author.id))
        data = await cursor.fetchone()
        await cursor.close()

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

        cursor = await sql.cursor()
        await cursor.execute("UPDATE masters SET discordid = %s, discordcode = 0, pendingdiscordid = 0 WHERE id = %s", (ctx.author.id, data['id']))
        await cursor.close()
        sql.close()

        await ctx.send("Your account is now verified!")

    @commands.command(help = "Manually link a discord account to an RCRP account.")
    @commands.guild_only()
    @commands.check(rcrp_check)
    @commands.check(management_check)
    async def manualverify(self, ctx, member: discord.Member = None, masteraccount: str = " "):
        if not member:
            await ctx.send("Invalid user.")
            return

        if member_is_verified(member) == True:
            await ctx.send(f"{member.mention} is already verified.")
            return

        if await account_name_valid(masteraccount) == False:
            await ctx.send("Invalid MA name")
            return

        if await account_verified(masteraccount) == True:
            await ctx.send("MA is already verified")
            return

        sql = await mysql_connect()
        cursor = await sql.cursor()
        await cursor.execute("UPDATE masters SET discordid = %s, discordcode = 0 WHERE Username = %s", (member.id, masteraccount))
        await cursor.close()
        sql.close()

        await member.add_roles(ctx.guild.get_role(verifiedrole))
        await ctx.send(f"{member.mention} has been manually verified as {masteraccount}")

    @commands.command(help = "Remove a discord account's verification status and unlink their RCRP account.")
    @commands.guild_only()
    @commands.check(rcrp_check)
    @commands.check(management_check)
    async def unverify(self, ctx, member: discord.Member = None):
        if not member:
            await ctx.send("Invalid user.")
            return

        if not account_verified(member):
            await ctx.send("This user is not verified")
            return

        sql = await mysql_connect()
        cursor = await sql.cursor()
        await cursor.execute("DELETE FROM discordroles WHERE discorduser = %s", (member.id, ))
        await cursor.execute("UPDATE masters SET discordid = 0 WHERE discordid = %s", (member.id, ))
        await cursor.close()
        sql.close()

        await member.remove_roles(*member.roles)
        await ctx.send(f"{member.mention} has been unverified.")

    @commands.command(help = "Remove the assigned discord ID from an RCRP account.")
    @commands.guild_only()
    @commands.check(rcrp_check)
    @commands.check(management_check)
    async def softunverify(self, ctx, discordid:int = None):
        if discordid == None:
            await ctx.send('Usage: !softunverify [discord ID]')
            return

        sql = await mysql_connect()
        cursor = await sql.cursor()
        await cursor.execute("UPDATE masters SET discordid = 0 WHERE discordid = %s", (discordid))

        if cursor.rowcount != 0:
            await ctx.send(f"Discord ID {discordid} has been unlinked from its MA.")
        else:
            await ctx.send(f"There are no accounts linked to Discord ID {discordid}")

        await cursor.close()
        sql.close()

def setup(bot):
    bot.add_cog(VerificationCog(bot))