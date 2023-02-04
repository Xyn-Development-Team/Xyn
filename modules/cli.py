import lightbulb
import hikari
import time
from lightbulb.ext import tasks
import os
import settings

cli = lightbulb.Plugin("cli")

async def command_handler(command):
    print(f"{command} was issued from the cli")
    command = str(command).split("-")
    if "say" in command[0]:
        message = str(command[1])
        to = command[2]
        await cli.bot.rest.create_message(to,message)
    elif "userinfo" in command[0]:
        user_id = int(command[1])
        user = await cli.bot.rest.fetch_user(user_id)
        username = user.username
        discriminator = user.discriminator
        creation_date = str(user.created_at)
        year = int(creation_date[0:4])
        month = creation_date[5:7]
        day = creation_date[8:10]
        hour = creation_date[11:13]
        minute = creation_date[14:16]
        current_year = int(time.strftime("%Y"))
        account_age = current_year - year
        if account_age > 1:
            print(f"User:{username}#{user.discriminator}\nAccount created at:{day}/{month}/{year} | {hour}:{minute} | Age : {current_year - year } years old")
        elif account_age == 1:
            print(f"User:{username}#{user.discriminator}\nAccount created at:{day}/{month}/{year} | {hour}:{minute} | Age : {current_year - year } year old")
        else:
            print(f"User:{username}#{user.discriminator}\nAccount created at:{day}/{month}/{year} | {hour}:{minute} | Age : {current_year - year } years old")
    elif "whoami" in command[0]:
        print(cli.app.get_me().username + "#" + cli.app.get_me().discriminator)
    elif "tokenswap" in command[0]: #Placeholder
        pass
    elif "swapenv" in command[0]: #Placeholder
        if "development" in command[1]:
            pass
        elif "retail" in command[1]:
            pass
    elif "reboot" in command[0]:
        with open("command.txt","w") as f:
            f.write("")
            f.close()
        os.system("python rebuild.py -OO")
    elif "shutdown" in command[0]:
        with open("command.txt","w") as f:
            f.write("")
            f.close()
        os.system("killall -9 python")
    elif "reload" in command[0]:
        print("Reloading modules...")
        if settings.modules.music:
            cli.bot.unload_extensions("modules.music")
            cli.bot.load_extensions("modules.music")
        if settings.modules.scraping:
            cli.bot.unload_extensions("modules.scraping")
            cli.bot.load_extensions("modules.scraping")
        if settings.modules.moderation:
            cli.bot.unload_extensions("modules.moderation")
            cli.bot.load_extensions("modules.moderation")
        if settings.modules.fun:
            cli.bot.unload_extensions("modules.fun")
            cli.bot.load_extensions("modules.fun")
        if settings.modules.debugging:
            cli.bot.unload_extensions("modules.debugging")
            cli.bot.load_extensions("modules.debugging")

@tasks.task(s=0.5,auto_start=True,max_consecutive_failures=float('inf'),wait_before_execution=True)
async def cli_reader():
    file = open("command.txt","r")
    command = file.read()
    if command != "":
        await command_handler(command)
        with open("command.txt","w") as f:
            f.write("")

def load(bot: lightbulb.BotApp):
    bot.add_plugin(cli)

def unload(bot):
    bot.remove_plugin(cli)