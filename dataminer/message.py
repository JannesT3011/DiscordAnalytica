from selectors import SelectorKey
import discord
from discord.ext import commands
from pytz import utc
from . import utcnow
from .bot_data import bot_messages
from .mentions import mentions_data

class Message(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        """EVENT IS CALLED WHEN A USER SEND A MESSAGE"""
        if not message.guild:
            return
        if message.author.bot:
            # TODO count bot messages
            bot_messages(message, self.bot.db)
            return
        if len(message.role_mentions) > 0:
            mentions_data(message, self.bot.db)
            return
        if message.content.startswith("da."):
            return
        roles = []
        for role in message.author.roles:
            roles.append(str(role))

        push_data = {"msgid": str(message.id), "timestamp": utcnow, "roles": roles, "channelid": str(message.channel.id), "attachments": True if len(message.attachments) > 0 else False}
        await self.bot.db.update_many({"_id": str(message.guild.id)}, {"$push": {"message": push_data}})
        return
    
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        roles = []
        for role in after.author.roles:
            roles.append(str(role))
        push_data = {"timestamp": utcnow, "roles": roles}
        await self.bot.db.update_many({"_id": str(after.guild.id)}, {"$push": {"message_edit": push_data}})
        return
    
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        roles = []
        for role in message.author.roles:
            roles.append(str(role))
        push_data = {"timestamp": utcnow, "roles": roles}
        await self.bot.db.update_many({"_id": str(message.guild.id)}, {"$push": {"message_delete": push_data}})
        return


def setup(bot):
    bot.add_cog(Message(bot))