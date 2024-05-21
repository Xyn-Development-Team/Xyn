import asyncio
import inspect
import platform
import time
import os
from sys import exit

import discord
from discord import app_commands
from colorama import Back, Fore, Style
from discord.ext import commands
from discord.ext.commands import has_permissions, is_owner
from typing import Literal

from dotenv import load_dotenv
load_dotenv()

import settings
import platform
import cpuinfo
import localization
import storage
import argparse

from requests import get
from shutil import rmtree

from typing import Literal
from github import Github, GithubException
import re

def generate_modulelist(quiet=False):
    print("Generating modulelist...")
    modulelist = {}
   
    if os.path.exists("./modules") and os.path.isdir("./modules"):
        for file in os.listdir("./modules"):
            file.rstrip(".py")
            if file in settings.modules.keys():
                modulelist[file] = settings.modules[file]
            else:
                modulelist[file] = True
        
        # Open the file for reading
        with open('settings.py', 'r') as file:
            lines = file.readlines()

        # Find the line where modules is defined
        for i, line in enumerate(lines):
            if 'modules =' in line:
                start_index = i
                break

        # Generate the new content with the updated modules dictionary
        new_content = ''.join(lines[:start_index]) + f"modules = {modulelist}\n"

        # Write the modified content back to the file
        with open('settings.py', 'w') as file:
            file.write(new_content)
        print("Your modulelist was updated!")
        return

def module_list():
    g = Github(os.getenv("github_username"), os.getenv("github_token"))
    repo = g.get_repo(re.sub("https://github.com/", "", settings.module_repo).lower())
    
    try:
        repo.get_contents("/.blacklist")
        blacklist = str(get(repo.get_contents("/.blacklist").download_url).content)
        blacklist = blacklist.lstrip("b'")
        blacklist = blacklist.rstrip("\\n'")
        blacklist = blacklist.split("\\n")
    except:
        blacklist = []

    for item in repo.get_contents("/"):
        if item.name in blacklist:
            continue
        print(f"{str(item.name).rstrip('.py')} / {'packaged' if item.type == 'dir' else 'legacy'}")
    
def module_uninstaller(name=str, gen_modulelist=True):
    if os.path.isdir(f"./modules/{name}"):
        rmtree(f"./modules/{name}")
    elif os.path.isfile(f"./modules/{name.rstrip(".py")}.py"):
        os.remove(f"./modules/{name.rstrip(".py")}.py")
    else:
        print(f"No module named \"{name}\"")
        return
    
    if gen_modulelist:
        generate_modulelist()

def module_installer(name=str, gen_modulelist=True):
    g = Github(os.getenv("github_username"), os.getenv("github_token"))
    repo = g.get_repo(re.sub("https://github.com/", "", settings.module_repo).lower())
    
    modules = name.split(",")
    
    for name in modules: 
        try:
            contents = repo.get_contents("/" + name)
        except GithubException as e:
            if e.status == 404:
                print(str(localization.internal.read("module_404", settings.language)).format(name=name))
                continue
            else:
                print(str(localization.internal.read("module_install_error", settings.language)).format(name=name, status=e.status, message=e.message))
        
        try:
            while len(contents) > 0:
                file_content = contents.pop(0)
                if file_content.type == 'dir':
                    dir_path = os.path.join("./modules", name, file_content.path[len(name) + 1:])  # Remove redundant '{name}/' part
                    if os.path.exists(dir_path):
                        rmtree(dir_path)  # Remove existing directory
                    os.makedirs(dir_path)
                    contents.extend(repo.get_contents(file_content.path))
                else:
                    file_path = os.path.join("./modules", name, file_content.path[len(name) + 1:])  # Remove redundant '{name}/' part
                    file_dir = os.path.dirname(file_path)
                    if not os.path.exists(file_dir):
                        os.makedirs(file_dir)
                    if os.path.exists(file_path):
                        os.remove(file_path)  # Remove existing file
                    with get(file_content.download_url) as response:
                        with open(file_path, 'wb') as file:
                            file.write(response.content)
                    print(str(localization.internal.read("module_downloading", settings.language)).format(path=file_content.path))
        except TypeError:
            file_path = os.path.join("./modules", name)
            name = str(name).rstrip(".py")
            with get(contents.download_url) as response:
                with open(file_path, 'wb') as file:
                    file.write(response.content)
            
        print(str(localization.internal.read("module_installed", settings.language)).format(module=name))
    
    if gen_modulelist:
        generate_modulelist()

class Bot(commands.Bot):
    """Initializes the bot and it's modules, as well as the error handler and argument parser"""
    def __init__(self, args=None):
        global token
        
        parser = argparse.ArgumentParser(description="Xyn Discord bot")
        parser.add_argument("--mode", default=settings.mode, choices=["development","retail"], help="Set the runtime mode (retail or development)")
        parser.add_argument("--token", default=None, help="Allows you to use a different token for this session")
        
        parser.add_argument("--setup", action="store_true")
        parser.add_argument("--generate-modulelist", action="store_true")
        parser.add_argument("--install","-i", help="Installs a module by name from the module repo defined in the settings.py")
        parser.add_argument("--uninstall","-u","-r", help="Uninstalls a module by it's name")
        parser.add_argument("--list", "-l", action="store_true", help="Lists all modules available on your module repository")
        
        if not args:
            args = parser.parse_args()
        else:
            args = parser.parse_args(args)
        
        if args.generate_modulelist:
            generate_modulelist()
            exit()
        
        if args.install:
            module_installer(args.install)
            exit()
            
        if args.uninstall:
            module_uninstaller(args.uninstall)
            exit()
        
        if args.mode and args.mode != settings.mode:
            settings.mode = args.mode

        if args.list:
            module_list()
            exit()
        
        if not os.path.isdir("./modules"):
            os.makedirs("./modules")
            
        if not os.listdir("./modules"):
            print("You don't have any modules installed!\nYou can install some by using the `--install` argument! Or even check some out using the `--list` argument!")
        
        if args.token:
            token = args.token
        elif settings.mode.lower() == "development":
            token = os.getenv("development_token")
        elif settings.mode.lower() == "retail":
            token = os.getenv("token")
        else:
            print(localization.internal.read("no_runtime", settings.language))
            exit()
        
        super().__init__(command_prefix=">.<>.<", intents=discord.Intents().all())

        @self.tree.command(name="reload", description="Reloads all bot modules!")
        @app_commands.describe(resync="Sync all commands")
        @commands.is_owner()
        async def reload(interaction: discord.Interaction, resync:Literal["Yes","No"]):
            await interaction.response.defer(thinking=True)
            for key, value in settings.modules.items():
                if value:
                    if os.path.isfile(f"modules/{key}.py"):
                        await self.reload_extension(f"modules.{key}")
                    elif os.path.isdir(f"modules/{key}"):
                        await self.reload_extension(f"modules.{key}.{key}")
                    else:
                        # The module {module}'s files are missing!!
                        print(str(localization.internal.read("module_missing",settings.language)).format(module=key))
            
            if resync == "Yes":
                await self.tree.sync()
            
            await interaction.followup.send("All modules were reloaded successfully!",ephemeral=True)

        @self.tree.command(name="language", description="Sets what language Xyn should use in it's responses!")
        @has_permissions(administrator=True)
        async def language(interaction: discord.Interaction, language:Literal[tuple(localization.languages.keys())]):
            if not interaction.guild:
                return await interaction.response.send_message(localization.internal.read("guild_only", str(interaction.locale).lower()))
                
            storage.guild.set(interaction.guild.id, "language", localization.languages[language])
            await interaction.response.send_message(str(localization.internal.read("language_set", localization.languages[language])).format(language=language))

        @self.tree.error
        async def on_app_command_error(interaction: discord.Interaction, error:discord.app_commands.CommandInvokeError):
            # Get the frame where the exception occurred
            frame = inspect.currentframe().f_back

            # Get information about the occurence
            line_number = frame.f_lineno
            file_path = inspect.getframeinfo(frame).filename
            filename = os.path.basename(inspect.getframeinfo(frame).filename)
            log = f"{time.strftime('%d/%m/%Y %H:%M:%S UTC')}\nException: {interaction.command.module}.{interaction.command.name}:\nFile: {filename} {'(External)' if file_path != os.getcwd() else ''}, line {line_number}\n{error.original}"
            
            if isinstance(error.original, discord.errors.InteractionResponded):
                # Interaction already acknowledged, {interaction.command.module}.{interaction.command.name}
                print(str(localization.internal.read("interaction_acknowledged",settings.language)).format(module=interaction.command.module,command=interaction.command.name))

            elif isinstance(error.original, discord.app_commands.MissingPermissions):
                # You don't have permission to use this command!
                await interaction.channel.send(localization.internal.read("user_no_permission",settings.language),ephemeral=True)
            
            elif isinstance(error.original, discord.app_commands.BotMissingPermissions):
                # I don't have permission to do this!
                await interaction.channel.send(localization.internal.read("bot_no_permission"),ephemeral=True)
            else:
                await interaction.channel.send(str(localization.internal.read("uncaught_exception",settings.language)).format(log=log))
                # "An uncaught exception has occurred, this occurrence has been automatically reported to your maintainer!:\nHere's the log:\n```{log}```
                logger = open(f"./logs/UncaughtException_{time.strftime('%d-%m-%Y %H:%M:%S UTC')}.txt","w",encoding="utf-8")
                logger.write(log)
                logger.close()

    async def setup_hook(self):
        for key, value in settings.modules.items():
            if value:
                if os.path.isfile(f"modules/{key}.py"):
                    await self.load_extension(f"modules.{key}")
                elif os.path.isdir(f"modules/{key}"):
                    await self.load_extension(f"modules.{key}.{key}")
                else:
                    # The module {module}'s files are missing!!
                    print(str(localization.internal.read("module_missing",settings.language)).format(module=key))
        if settings.resync:
            await self.tree.sync()

    # Let's make sure we'll always have a language set for any new guilds
    async def on_guild_join(self, guild):
        if not storage.guild.read(guild.id, "language"):
            storage.guild.set(guild.id, "language", settings.language)
        if storage.guild.read(guild.id, "name") != guild.name and settings.guilds["log_names"]:
            storage.guild.set(guild.id, "name", guild.name)

    # In case a guild doesn't have a language set and a command is used.
    async def on_interaction(self, interaction:discord.Interaction):
        if interaction.guild:
            if not storage.guild.read(interaction.guild.id, "language"):
                storage.guild.set(interaction.guild.id, "language", settings.language)
            if storage.guild.read(interaction.guild.id, "name") != interaction.guild.name and settings.guilds["log_names"]:
                storage.guild.set(interaction.guild.id, "name", interaction.guild.name)

    async def on_ready(self):
        if not os.path.isdir("./logs"):
            os.makedirs("./logs")
        
        if settings.guilds["startup_check"]:
            print("Checking guilds for broken or missing settings files...")
            start_time = time.time()
            for guild in self.guilds:
                if not storage.guild.read(guild.id, "language"):
                    storage.guild.set(guild.id, "language", settings.language)
                    storage.guild.set(guild.id, "name", guild.name)
            print(f"Finished checks in {round(time.time() - start_time,2)}s")
        
        #Status task, updates the bot's presence every minute
        async def status_task(self):
            while True:
                await self.change_presence(activity=discord.Activity(type=discord.ActivityType.streaming,name="past you nerds!",url="https://www.youtube.com/watch?v=HZCKddHYgPM"))
                await asyncio.sleep(60)
                await self.change_presence(activity=discord.Activity(type=discord.ActivityType.playing,name="with you nerds!"))
                await asyncio.sleep(60)
                await self.change_presence(activity=discord.Activity(type=discord.ActivityType.playing,name="hide and seek with Fae!"))
                await asyncio.sleep(60)

        bot.loop.create_task(status_task(self))
        prfx = (Back.BLACK + Fore.MAGENTA + time.strftime("%H:%M:%S UTC", time.gmtime()) + Back.RESET + Fore.WHITE + Style.BRIGHT + " ")
        # prfx + f" Logged in as {Fore.MAGENTA}{self.user.name}{Fore.RESET}"
        print(prfx + str(localization.internal.read("logged_as",settings.language)).format(color=Fore.MAGENTA,user=self.user.name,reset=Fore.RESET))
        # prfx + f" Running on {Fore.GREEN}{settings.mode.lower()}{Fore.RESET} mode"
        print(prfx + str(localization.internal.read("running_on",settings.language)).format(color=Fore.GREEN,mode=str(localization.internal.read(settings.mode.lower(),settings.language)).lower(),reset=Fore.RESET))
        # prfx + f" OS: {Fore.CYAN}{platform.platform()} / {platform.release()}{Fore.RESET}"
        print(prfx + str(localization.internal.read("os",settings.language)).format(color=Fore.CYAN,os=platform.platform(),release=platform.release(),reset=Fore.RESET))
        # prfx + f" CPU: {Fore.CYAN}{cpuinfo.get_cpu_info()['brand_raw']}{Fore.RESET}"
        print(prfx + str(localization.internal.read("cpu",settings.language)).format(color=Fore.CYAN,cpu=cpuinfo.get_cpu_info()['brand_raw'],reset=Fore.RESET))
        # prfx + " Python Version " + Fore.YELLOW + str(platform.python_version()) + Fore.WHITE"
        print(prfx + str(localization.internal.read("python_version",settings.language)).format(color=Fore.YELLOW,version=str(platform.python_version()),reset=Fore.RESET))
        # prfx + " Discord.py Version " + Fore.YELLOW + discord.__version__ + Fore.RESET"
        print(prfx + str(localization.internal.read("discord.py_version")).format(color=Fore.YELLOW,version=discord.__version__,reset=Fore.RESET))

bot = Bot()
bot.run(token)