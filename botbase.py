import pyfiglet
import contextlib
import re
import pymongo
import os

from aiohttp import ClientSession
import discord
from discord.ext import commands

from config import Config
from utils.error_logging import error_to_embed

async def get_custom_prefix( bot, message):
        col = bot.db["prefixes"]
        if not message.guild:
            return "t."
        val = col.find({"_id": message.guild.id})
        val_list = list(val)
        if len(val_list[0]) != 2:
            return "t."
        
        elif len(val_list[0]) == 2:
            val_dct = val_list[0]
            return val_dct['prefix']

class Bot(commands.Bot):
    def __init__(
        self,
        *,
        description: str,
        config: Config,
    ):
        allowed_mentions = discord.AllowedMentions(
            roles=False,
            everyone=False,
            users=True,
        )
        super().__init__(
            command_prefix=get_custom_prefix,
            intents=discord.Intents.all(),
            allowed_mentions=allowed_mentions,
            description=description,
            token="No.",
        )
        os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
        self.config: Config = config
        self.ignore_dms: bool = False
        self.respond_to_ping: bool = True
        self.session = ClientSession(loop=self.loop)
        self.mongo_client = pymongo.MongoClient(self.config.database_url)
        self.db = self.mongo_client["Bot1"]

        self.load_extensions()
        self.load_extension("jishaku")

    @property
    def log_webhook(self) -> discord.Webhook:
        return discord.Webhook.partial(
            id=self.config.log_webhook_id, 
            token=self.config.log_webhook_token,
            session=self.session,
        )


    def load_extensions(self):
        import os
        for ext in os.listdir("cogs"):
            if ext.endswith(".py"):
                try:
                    self.load_extension(f"cogs.{ext[:-3]}")
                except Exception as e:
                    print(e)

    def run(self) -> None:
        return super().run(self.config.bot_token, reconnect=True)

    
    async def on_ready(self):
        print(pyfiglet.figlet_format(self.user.name))
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print(f"Connected to: {len(self.guilds)} guilds")
        print(f"Connected to: {len(self.users)} users")
        print(f"Connected to: {len(self.cogs)} cogs")
        print(f"Connected to: {len(self.commands)} commands")

    async def on_message(self, msg):
        if msg.author.bot:
            return

        if self.ignore_dms and not msg.guild and not await self.is_owner(msg.author):
            return

        if msg.guild and msg.guild.me and not msg.channel.permissions_for(msg.guild.me).send_messages:  # type: ignore
            return

        user_id = self.user.id
        if self.respond_to_ping and msg.content in (f"<@{user_id}>", f"<@!{user_id}>"):
            return await msg.reply(
                "Hi use my mention as prefix (or my slash commands)."
            )

        await self.process_commands(msg)

    async def on_error(self, event_method: str, *args, **kwargs) -> None:
        embeds = error_to_embed()
        context_embed = discord.Embed(
            title="Context", description=f"**Event**: {event_method}", color=discord.Color.red()
        )
        await self.log_webhook.send(embeds=[*embeds, context_embed])

    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        if isinstance(error, commands.CommandNotFound):
            return
        if not isinstance(error, commands.CommandInvokeError):
            title = " ".join(
                re.compile(r"[A-Z][a-z]*").findall(error.__class__.__name__)
            )
            return await ctx.send(
                embed=discord.Embed(title=title, description=str(error), color=discord.Color.red())
            )

        embed = discord.Embed(
            title="Error",
            description="An unknown error has occurred and my developer has been notified of it.",
            color=discord.Color.red(),
        )
        with contextlib.suppress(discord.NotFound, discord.Forbidden):
            await ctx.send(embed=embed)

        traceback_embeds = error_to_embed(error)

        info_embed = discord.Embed(
            title="Message content",
            description="```\n" + discord.utils.escape_markdown(ctx.message.content) + "\n```",
            color=discord.Color.red(),
        )

        value = (
            (
                "**Name**: {0.name}\n"
                "**ID**: {0.id}\n"
                "**Created**: {0.created_at}\n"
                "**Joined**: {0.me.joined_at}\n"
                "**Member count**: {0.member_count}\n"
                "**Permission integer**: {0.me.guild_permissions.value}"
            ).format(ctx.guild)
            if ctx.guild
            else "None"
        )

        info_embed.add_field(name="Guild", value=value)
        if isinstance(ctx.channel, discord.TextChannel):
            value = (
                "**Type**: TextChannel\n"
                "**Name**: {0.name}\n"
                "**ID**: {0.id}\n"
                "**Created**: {0.created_at}\n"
                "**Permission integer**: {1}\n"
            ).format(ctx.channel, ctx.channel.permissions_for(ctx.guild.me).value)
        else:
            value = (
                "**Type**: DM\n" "**ID**: {0.id}\n" "**Created**: {0.created_at}\n"
            ).format(ctx.channel)

        info_embed.add_field(name="Channel", value=value)

        value = (
            "**Name**: {0}\n" "**ID**: {0.id}\n" "**Created**: {0.created_at}\n"
        ).format(ctx.author)

        info_embed.add_field(name="User", value=value)

        await self.log_webhook.send(embeds=[*traceback_embeds, info_embed])
    

    async def on_guild_join(self, guild):
        col = self.db["prefixes"]
        val = col.find({"_id": guild.id})
        if len(list(val)) == 0:
            col.insert_one({"_id": guild.id, "prefix": "t."})
            return
    

