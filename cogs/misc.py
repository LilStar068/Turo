import discord
import time


from discord.ext import commands


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        """ Pong! """
        before = time.monotonic()
        before_ws = int(round(self.bot.latency * 1000, 1))
        message = await ctx.send("🏓 Pong")
        ping = (time.monotonic() - before) * 1000
        await message.edit(content=f"🏓 WS: {before_ws}ms  |  REST: {int(ping)}ms")

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def invite(self, ctx):
        f""" "Invite {self.bot.user.name} to your server!"""
        await ctx.reply(
            embed=discord.Embed(
                title=f"Invite {self.bot.user.name} 💖",
                description="Thank you so much!",
                color=discord.Color.blue(),
                url=f"https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot%20applications.commands",
            )
        )
    


def setup(bot):
    bot.add_cog(Misc(bot))
