import objdict
import os
import inspect

languages = {
    "":"en-us",
    "English":"en-us",
    "American English":"en-us",
    "Japanese":"jp",
    "日本語":"jp",
    "Português":"pt-br",
    "Portuguese":"pt-br",
}

def read(file,id):
    try:
        with open(f"{file}","r") as locale:
            data = objdict.loads(str(locale.read()))
            try:
                return data[id]
            except KeyError:
                print(f"| WARN | The locale: {file} doesn't contain the string ID {id}\nreading from the default en-us.json")
                try:
                    with open(f"./localization/en-us.json","r") as locale:
                        data = objdict.loads(str(locale.read()))
                        return data[id]
                except:
                    raise Exception(f"| ERROR | There's no {id} in the en-us.json file!")

    except FileNotFoundError:
        try:
            with open(f"./localisation/en-us.json","r") as locale:
                data = objdict.loads(str(locale.read()))
                return data[id]
        except:
            raise

def locale(id:str,lang="en-us"):
    """## This uses the locale of the current module
    `id`: String ID, this is how the string is mapped! ex:\"only_guild\"
    `lang`: This is the language which the string returned should be. This is passed in alpha 2 language codes!"""

    module_folder = os.path.dirname(inspect.currentframe().f_back.f_code.co_filename)

    try:
        with open(f"{module_folder}/localization/{str(lang).lower()}.json","r") as locale:
            data = objdict.loads(str(locale.read()))
            try:
                return data[id]
            except KeyError:
                print(f"| WARN | The locale: {module_folder}/localization/{lang.lower}.json doesn't contain the string ID {id}\nreading from the default en-us.json")
                with open(f"{module_folder}/localization/en-us.json","r") as locale:
                    data = objdict.loads(str(locale.read()))
                    return data[id]
    except FileNotFoundError:
        with open(f"{module_folder}/localization/en-us.json","r") as locale:
            data = objdict.loads(str(locale.read()))
            try:
                return data[id]
            except KeyError:
                print(f"| WARN | The locale: {module_folder}/localization/{lang.lower}.json doesn't contain the string ID {id}\nreading from the default en-us.json")
                with open(f"{module_folder}/localization/en-us.json","r") as locale:
                    data = objdict.loads(str(locale.read()))
                    return data[id]

class internal:
    def locale(id:str,lang="en-us"):
        """`id`: String ID, this is how the string is mapped! ex:\"only_guild\"
        `lang`: This is the language which the string returned should be. This is passed in alpha 2 language codes!"""

        if not os.path.isfile(f"./localization/{lang.lower()}.json"):
            print(f"| WARN | The file ./localization/{lang.lower()}.json doesn't exist!\nUsing ./localization/en-us.json instead!")
            lang = "en-us"

        with open(f"./localization/{lang.lower()}.json") as locale:
            try:
                data = objdict.loads(str(locale.read()))
                return data[id]
            except:
                print(f"| WARN | The ID {id} wasn't found in {lang.lower()}.json\nResponding with default en-us.json")
            try:
                with open(f"./localization/en-us.json") as locale:
                    data = objdict.loads(str(locale.read()))
                    return data[id]
            except:
                raise Exception(f"| ERROR | There's no {id} in the en-us.json file!")
        
