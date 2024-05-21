mode = "Development" #Development, Retail
language = "en-us" # Check ./localization for the available languages.
resync = True # Updates all slash commands on startup, recommended to leave at `False` unless you're implementing new commands.
module_repo = "https://github.com/Xyn-Development-Team/Xyn-Module-Repo" # Repository used by Xyn to install modules.

guilds = {
    "startup_check":True, # Checks if every guild has a language defined, and if not it applies Xyn's language.
    "log_names":True
}

music = {
    "cache":100
}

# Module list
# Here you can enable or disable Xyn's modules!
modules = {'fun': True, 'music': True, 'osu': True, 'scraping': True, 'social': True}
