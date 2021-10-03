import discord

from discord.ext import commands
from utils import default


class MemberID(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            m = await commands.MemberConverter().convert(ctx, argument)
        except commands.BadArgument:
            try:
                return int(argument, base=10)
            except ValueError:
                raise commands.BadArgument(
                    f"{argument} is not a valid member or member ID."
                ) from None
        else:
            return m.id


class Mod(commands.Cog):
    """Keep Your server safe."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = None):
        """Kicks a user from the current server."""
        try:
            await member.kick(reason=default.responsible(ctx.author, reason))
            await ctx.send(default.actionmessage("kicked"))
        except Exception as e:
            await ctx.send(e)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: MemberID, *, reason: str = None):
        """Bans a user from the current server."""
        try:
            await ctx.guild.ban(
                discord.Object(id=member),
                reason=default.responsible(ctx.author, reason),
            )
            await ctx.send(default.actionmessage("banned"))
        except Exception as e:
            await ctx.send(e)

    @commands.command()
    @commands.max_concurrency(1, per=commands.BucketType.user)
    @commands.has_permissions(ban_members=True)
    async def massban(self, ctx, members: commands.Greedy[MemberID], reason: str):
        """Mass bans multiple members from the server."""
        try:
            for member_id in members:
                await ctx.guild.ban(
                    discord.Object(id=member_id),
                    reason=default.responsible(ctx.author, reason),
                )
            await ctx.send(default.actionmessage("massbanned", mass=True))
        except Exception as e:
            await ctx.send(e)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, member: MemberID, *, reason: str = None):
        """Unbans a user from the current server."""
        try:
            await ctx.guild.unban(
                discord.Object(id=member),
                reason=default.responsible(ctx.author, reason),
            )
            await ctx.send(default.actionmessage("unbanned"))
        except Exception as e:
            await ctx.send(e)

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def setprefix(self, ctx, prefix: str):
        col = self.bot.db["prefixes"]
        col.update_one({"_id": ctx.guild.id}, {"$set": {"prefix": prefix}}, upsert=True)
        await ctx.send("Done, I have changed my prefix here to {0}".format(prefix))


def setup(bot):
    bot.add_cog(Mod(bot))
