#In which mode should Xyn run?
mode = "Development" #Retail, Development

#Should the logo in the CLI Terminal appear?
logo = True

#Here you can enable/disable all of Xyn's addons, and maybe even add a couple of your own? >.o
modules = {
    "fun":True,
    "scraping":True,
    "music":True,
    "moderation":True,
    "osu":True,
    "about":True,
    "analytics":True
    }

class music:
    max_rewind = 5 #How many songs that have to play before Xyn starts to wipe the list (Default is 5)
    autostart_lavalink = False #This starts Lavalink alongside Xyn, whenever the music module is enabled, this **will** unite both outputs into a single terminal!

#Here you may fill this with details about this deployment of Xyn
class deploy:
    codename = "Vanilla"
    development_codename = "Betafish"

    maintainers = "XDT (Xyn Development Team! >.<)"

    if mode.lower() == "development":
        codename = development_codename

    #Here you may explain why Xyn asks for `x` permission
    permissions_usage = {"General -> Manage Webhooks":f"Xyn ({codename}) uses these permissions for commands such as `/fun persona` and for swapping it's profile details on a command-basis manner",
                         "Text -> Manage Messages":f"Xyn ({codename}) uses this permission for the command `/moderation purge` which is a command that let's a user of same permission to bulk delete a specified amount of messages",
                         "Text -> Send Messages":f"Xyn ({codename}) uses this permission to reply to all of it's commands!",
                         "Text -> Embed Links":f"Xyn ({codename}) uses this permission to create embeds by simply sending a URL, used for all scraping commands!",
                         "Text -> Attach Files":f"Xyn ({codename}) uses this permission to attach images to it's replys, used by all image generation commands!",
                         "Text -> Read Message History":f"Xyn ({codename}) uses this permission for the context-menu command 'Quote this!'",
                         "Text -> Use External Emojis":f"Xyn ({codename}) uses this permission to load a ton of easy to access custom elements, such as 'loading screens' and others",
                         "Voice -> Connect":f"Xyn ({codename}) uses this permission to connect to Voice Channels, used by all music commands!",
                         "Voice -> Speak":f"Xyn ({codename}) uses this permission to play the music in Voice channels, used by most music commands!"
                         }

    credits = {"Project Lead":"Nyx_Chan",
               "Lead Developer":"Moonlight Dorkreamer 🌓",

               "Architecture Designers":"Nyx_Chan, Moonlight Dorkreamer 🌓",

               "Lead Branding/Design":"Moonlight Dorkreamer 🌓",
               
               }#"Beta testers":"Moonlight Dorkreamer 🌓, Nyx_Chan, Tal o Maculado (Tô suave), SK Dino, Haru 乄, "}
