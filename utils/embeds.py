import discord
from discord.embeds import EmptyEmbed

def success_embed(title = EmptyEmbed, d = EmptyEmbed):
    return discord.Embed(title=title, description=d, color=discord.Color.blue())
