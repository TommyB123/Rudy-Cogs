import discord
import aiomysql
import os
from .config import mysqlconfig
from redbot.core import commands

#rcrp guild ID
rcrpguildid = 93142223473905664

async def rcrp_check(ctx: commands.Context):
    return ctx.guild.id == rcrpguildid

class pending_model():
    """Pending model data"""
    model_id: int
    reference_model: int
    dff_url: str
    txd_url: str
    model_type: str
    model_path: str

#empty dict for pending model data. key will be the model's ID
models = {}

#path of RCRP models
rcrp_model_path = "/home/rcrp/domains/cdn.redcountyrp.com/public_html/rcrp/"

class RCRPModelManager(commands.Cog):
    """RCRP Model Manager"""
    def __init__(self, bot: discord.Client):
        self.bot = bot

    def get_model_range_for_type(self, type: str):
        """Returns the valid range of model IDs for a specific type"""
        type = type.upper()
        if type == 'PED':
            return 20000, 30000
        elif type == 'OBJECT':
            return -30000, -1000
        else:
            return -1, -1
    
    def get_model_type_folder(self, type: str):
        """Returns the folder used for a specific model type"""
        type = type.upper()
        if type == 'PED':
            return 'peds'
        elif type == 'OBJECT':
            return 'objects'
        else:
            return '' 
        
    def model_type_int(self, type: str):
        """Returns the reference constant for model types that's used in the MySQL database/RCRP script"""
        type = type.upper()
        if type == 'PED':
            return 0
        elif type == 'OBJECT':
            return 1
        else:
            return -1
    
    def model_type_name(self, type: int):
        """Returns the reference string for model types based on the constant used in the MySQL database/RCRP script"""
        if type == 0:
            return 'PED'
        elif type == 1:
            return 'OBJECT'
        else:
            return ''
    
    async def is_valid_model(self, modelid: int):
        """Queries the MySQL database to see if a model ID exists"""
        sql = await aiomysql.connect(**mysqlconfig)
        cursor = await sql.cursor()
        await cursor.execute("SELECT NULL FROM models WHERE modelid = %s", (modelid, ))
        rows = cursor.rowcount
        await cursor.close()
        sql.close()

        return rows != 0
    
    def is_valid_model_type(self, type: str):
        """Checks if the supplied string matches a valid model type. Valid types are 'PED' or 'OBJECT'"""
        temp_type = type.upper()
        if temp_type != 'PED' and temp_type != 'OBJECT':
            return False
        else:
            return True

    @commands.group()
    @commands.guild_only()
    @commands.is_owner()
    async def modelmanager(self, ctx):
        """Manage and add new custom models"""
        pass

    @modelmanager.command()
    @commands.guild_only()
    @commands.is_owner()
    async def addmodel(self, ctx: commands.Context, modelid: int, reference_id: int, folder: str, type: str, dff_url: str, txd_url: str):
        """Adds a new model to the pending models list"""
        if self.is_valid_model_type(type) == False:
            await ctx.send('Invalid type.')
            return

        min, max = self.get_model_range_for_type(type)
        if modelid not in range(min, max):
            await ctx.send(f'Invalid model ID for type {type}. Please use a range of {min} to {max} for this type.')
            return
        
        if await self.is_valid_model(modelid) == True:
            await ctx.send(f'The model {modelid} is already present on the server.')
            return
        
        model_info = pending_model()
        model_info.model_id = modelid
        model_info.reference_model = reference_id
        model_info.dff_url = dff_url
        model_info.txd_url = txd_url
        model_info.model_type = type
        model_info.model_path = folder
        models[modelid] = model_info
        await ctx.send(f'Model ID {modelid} has been added to the pending models list. Use !modelmanager finalize when you are ready to download the pending models to the server and add them in-game.')
    
    @modelmanager.command()
    @commands.guild_only()
    @commands.is_owner()
    async def removependingmodel(self, ctx: commands.Context, modelid: int):
        """Removes a model from the list of current pending models"""
        if len(models) == 0:
            await ctx.send('There are currently no pending models.')
            return

        if modelid not in models:
            await ctx.send('No pending model found with that ID.')
            return

        del models[modelid]
        await ctx.send(f'Model ID {modelid} has been removed from the pending models list.')

    @modelmanager.command()
    @commands.guild_only()
    @commands.is_owner()
    async def deletemodel(self, ctx: commands.Context, modelid: int, deletefile: bool = False):
        """Removes a custom model from the server (RCRP restart required for full effect)"""
        if await self.is_valid_model(modelid) == False:
            await ctx.send(f'{modelid} is not a model ID that is used on the server.')
            return

        sql = await aiomysql.connect(**mysqlconfig)
        cursor = await sql.cursor()
        await cursor.execute("DELETE FROM models WHERE modelid = %s", (modelid, ))
        await cursor.close()
        sql.close()
        
        #todo: file management on the OS
        await ctx.send(f'Model {modelid} has been deleted from the MySQL database and also the server. This will not take full effect until the next RCRP restart.')

    @modelmanager.command()
    @commands.guild_only()
    @commands.is_owner()
    async def viewpendingmodel(self, ctx: commands.Context, modelid: int):
        """Views the information of a pending model that has not been sent to the server yet"""
        if len(models) == 0:
            await ctx.send('There are currently no pending models.')
            return

        if modelid not in models:
            await ctx.send('No pending model found with that ID.')
            return
        
        model_info: pending_model = models[modelid]
        embed = discord.Embed(title = f'Pending Model Information ({modelid})', color = ctx.author.color)
        embed.add_field(name = 'Reference ID', value = model_info.reference_model, inline = False)
        embed.add_field(name = 'TXD URL', value = model_info.txd_url, inline = False)
        embed.add_field(name = 'DFF URL', value = model_info.dff_url, inline = False)
        embed.add_field(name = 'Model Type', value = model_info.model_type, inline = False)
        embed.add_field(name = 'Model Path', value = model_info.model_path, inline = False)
        await ctx.send(embed = embed)
    
    @modelmanager.command()
    @commands.guild_only()
    @commands.is_owner()
    async def fetchmodelinfo(self, ctx: commands.Context, modelid: int):
        """Retrieves information about an existing model from the MySQL database"""
        if await self.is_valid_model(modelid) == False:
            await ctx.send(f'{modelid} is not a valid model ID used on the server.')
            return
        
        sql = await aiomysql.connect(**mysqlconfig)
        cursor = await sql.cursor(aiomysql.DictCursor)
        await cursor.execute("SELECT * FROM models WHERE modelid = %s", (modelid, ))
        data = await cursor.fetchone()
        await cursor.close()
        sql.close()

        embed = discord.Embed(title = f'Model Information ({modelid})', color = ctx.author.color)
        embed.add_field(name = 'TXD', value = data['txd_name'], inline = False)
        embed.add_field(name = 'DF', value = data['dff_name'], inline = False)
        embed.add_field(name = 'Model Type', value = self.model_type_name(data['modeltype']), inline = False)
        embed.add_field(name = 'Model Path', value = data['folder'], inline = False)
        await ctx.send(embed = embed)
    
    @modelmanager.command()
    @commands.guild_only()
    @commands.is_owner()
    async def finalize(self, ctx: commands.Context):
        """Downloads all pending models and sends a signal to the RCRP gamemode to check for any existing"""
        if len(models) == 0:
            await ctx.send('There are currently no pending models.')
            return

        model_list = list(models.values())
        models.clear()

        #todo: add server downloading
        
        sql = await aiomysql.connect(**mysqlconfig)
        cursor = await sql.cursor()
        for model in model_list:
            await cursor.execute("INSERT INTO models (modelid, modeltype, dff_name, txd_name, folder) VALUES (%s, %s, %s, %s, %s)",
                (model.model_id, self.model_type_int(model.model_type), model.dff_url, model.txd_url, model.model_folder))

        #todo: add RCRP gamemode notification thing

        await cursor.close()
        sql.close()
        models.clear()

        modelcount = len(model_list)
        await ctx.send(f'{modelcount} {"models" if modelcount != 1 else "model"} has been successfully downloaded and added to RCRP.')

    @modelmanager.group()
    @commands.guild_only()
    @commands.is_owner()
    async def set(self, ctx: commands.Context, modelid: int, type: str):
        """Set various attributes for an existing model"""
        pass

    
    @set.command()
    @commands.guild_only()
    @commands.is_owner()
    async def dff(self, ctx: commands.Context, modelid: int, texturename: str):
        """Updates the DFF of an existing model"""
        await ctx.send('wip')

    @set.command()
    @commands.guild_only()
    @commands.is_owner()
    async def txd(self, ctx: commands.Context, mdoelid: int, txdname: str):
        """Updates the TXD of an existing model"""
        await ctx.send('wip')
    
    @set.command()
    @commands.guild_only()
    @commands.is_owner()
    async def folder(self, ctx: commands.Context, modelid: int, folder: str):
        """Updates the folder of an existing model"""
        await ctx.send('wip')
    
    @set.command()
    @commands.guild_only()
    @commands.is_owner()
    async def type(self, ctx: commands.Context, modelid: int, type: str):
        """Updates the type of an existing model (skin or object)"""
        await ctx.send('wip')
