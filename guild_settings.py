import os
import configparser

import localization.enus as English
import localization.ja as Japanese
import localization.ptbr as Portuguese
import localization.uwuify.enus as EnglishUwU

def set_language(id,language):
    config = configparser.ConfigParser()
    if not os.path.isfile(f"./data/guilds{id}.ini"):
        if not os.path.isdir("./data/guilds"):
            os.makedirs("./data/guilds")
        config.add_section("Info")
        config["Info"]["GuildID"] = str(id)
        config.add_section("locale")
    config["locale"]["language"] = language
    with open(f"./data/guilds/{id}.ini","w") as f:
        config.write(f)

def guild_language(id):
    config = configparser.ConfigParser()
    try:
        config.read_file(open(rf'./data/guilds/{id}.ini'))
        return config.get('locale', 'language')
    except:
        set_language(id, "English")
        return "English"

def get_uwu(id):
    config = configparser.ConfigParser()
    try:
        config.read_file(open(rf'./data/guilds/{id}.ini'))
        if config.get('locale', 'uwu') == "True":
            return True
        else:
            return False
    except:
        set_uwu(id,False)
        return False

def set_uwu(id,enabled=False):
    config = configparser.ConfigParser()
    if guild_language(id) == "English":
        config.read_file(open(rf'./data/guilds/{id}.ini'))
        config.set("locale","uwu",f"{str(enabled)}")
        with open(f"./data/guilds/{id}.ini","w") as f:
            config.write(f)
    else:
        return "English Only"

def text(string,lang,uwu=False):
    if lang == "Portuguese":
        locale = Portuguese.locale
    elif lang == "Japanese":
        locale = Japanese.locale
    elif lang == "English":
        if uwu:
            locale = EnglishUwU.locale
        else:
            locale = English.locale
    else:
        return "Invalid Language!"
    return str(locale.get(string))

def set(id,section,option,value=None,default=None):
    config = configparser.ConfigParser()
    if not os.path.isfile(f"./data/guilds{id}.ini"):
        set_language(id,"English")
    if not value:
        value = default
    try:
        config.read_file(open(rf'./data/guilds/{id}.ini'))
        config.set(section,option,value)
    except configparser.NoSectionError:
        config.add_section(f"{section}")
        #config.set(section,option,value)
        config[f"{section}"][f"{option}"] = value
    with open(f"./data/guilds/{id}.ini","w") as f:
        config.write(f)
        f.close()

def read(id,section,option,create=False,create_default=None):
    config = configparser.ConfigParser()
    try:
        config.read_file(open(rf'./data/guilds/{id}.ini'))
        return config.get(str(section), str(option))
    except configparser.NoSectionError:
        if create:
            set(id,section,option,create_default)
            config.read_file(open(rf'./data/guilds/{id}.ini'))
            return config.get(f'{section}',f'{option}')
        else:
            return None