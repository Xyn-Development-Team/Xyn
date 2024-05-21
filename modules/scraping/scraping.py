class module:
    name = "Scraping"
    cog_name = "scraping"
    description = "Data scraping commands"
    author = "Moonlight Dorkreamer 🌓"
    xyn_version = "V3"
    version = "04042024"

import os

if __name__ == "__main__":
    # This is supposed to be imported by Xyn! You dummy!!!
    # We can't really localize this, since loading localization with this being directly executed would crash :c
    print("This is supposed to be imported by Xyn! You dummy!!!")
    os._exit(1)
else:
    import discord
    from discord import app_commands
    from discord.ext import commands
    from typing import Literal
    from typing import Optional
    from os import getenv
    import localization
    import settings
    import storage

class scraping(commands.GroupCog, name=module.cog_name):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()

        # User menu
        bot.tree.add_command(app_commands.ContextMenu(name="Fetch pfp", callback=self.get_pfp_user_menu))
        bot.tree.add_command(app_commands.ContextMenu(name="Fetch banner", callback=self.get_banner_user_menu))

        # Message menu
        bot.tree.add_command(app_commands.ContextMenu(name="Fetch pfp", callback=self.get_pfp_message_menu))
        bot.tree.add_command(app_commands.ContextMenu(name="Fetch banner", callback=self.get_banner_message_menu))

    async def get_pfp_user_menu(self, interaction:discord.Interaction, user:discord.User):
        return await interaction.response.send_message(user.display_avatar.url, ephemeral=True)

    async def get_banner_user_menu(self, interaction:discord.Interaction, user:discord.User):
        if interaction.guild:
            language = storage.guild.read(interaction.guild.id,"language")
        else:
            language = str(interaction.locale).lower()

        return await interaction.response.send_message(user.banner.url if user.banner else str(localization.external.read("no_banner", language)).format(user=user.mention), ephemeral=True)

    async def get_pfp_message_menu(self, interaction:discord.Interaction, message:discord.Message):
        return await interaction.response.send_message(message.author.display_avatar.url, ephemeral=True)

    async def get_banner_message_menu(self, interaction:discord.Interaction, message:discord.Message):
        if interaction.guild:
            language = storage.guild.read(interaction.guild.id,"language")
        else:
            language = str(interaction.locale).lower()

        return await interaction.response.send_message(message.author.banner.url if message.author.banner else str(localization.external.read("no_banner", language)).format(user=message.author.mention), ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    print(localization.external.read("setup.loaded",settings.language))
    await bot.add_cog(scraping(bot))
