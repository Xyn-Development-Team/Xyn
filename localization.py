from objdict import ObjDict
import objdict
import os
import settings
import inspect

languages = {
    "English":"en-us",
    "Deutsch":"de-de",
    "Português":"pt-br",
    "UwU":"en-uwu"
}

class internal:
    def read(string_id,lang="en-us"):
        # Check if folder even exists
        if not os.path.isdir("./localization"):
            print("| Xyn/localization | The localization folder is missing!!")
            return None

        # In case we're missing just the requested language
        if not os.path.isfile(f"./localization/{lang}.json") and lang != "en-us":
            print(f"| Xyn/localization | No localization files for {lang}")
            lang = "en-us"

            # In case we're missing *all* language files
            if not os.listdir("./localization"):
                print("| Xyn/localization | There are no translation files present!!")
                return None
            else:
                # There's hope to at least return something!
                lang = str(os.listdir("./localization")[0]).replace(".json","")

        with open(f"./localization/{lang}.json","r") as file:
            data = objdict.loads(str(file.read()))
            try:
                return data[string_id]
            # In case the string we want isn't available in the requested language
            except KeyError:
                print(f"| Xyn/localization | \"{string_id}\" isn't available in {lang}!")
                if lang != "en-us":
                    try:
                        with open(f"./localization/en-us.json","r") as file:
                            data = objdict.loads(str(file.read()))
                            return data[string_id]
                    except KeyError:
                        print(f"| Xyn/localization | \"{string_id}\" also isn't available in en-us!!")
                        return None

class external:
    def read(string_id,lang="en-us"):

        module_root = os.path.dirname(inspect.currentframe().f_back.f_code.co_filename)

        # Check if folder even exists
        if not os.path.isdir(f"{module_root}/localization"):
            print("| Xyn/localization | The localization folder is missing!!")
            return None

        # In case we're missing just the requested language
        if not os.path.isfile(f"{module_root}/localization/{lang}.json"):
            print(f"| Xyn/localization | No localization files for {lang}")
            lang = "en-us"

            # In case we're missing *all* language files
            if not os.listdir(f"{module_root}/localization"):
                print("| Xyn/localization | There are no translation files present!!")
                return None
            else:
                # There's hope to at least return something!
                lang = str(os.listdir(f"{module_root}/localization")[0]).replace(".json","")

        with open(f"{module_root}/localization/{lang}.json","r") as file:
            data = objdict.loads(str(file.read()))
            try:
                return data[string_id]
            # In case the string we want isn't available in the requested language
            except KeyError:
                print(f"| Xyn/localization | \"{string_id}\" isn't available in {lang}!")
                try:
                    with open(f"{module_root}/localization/en-us.json","r") as file:
                        data = objdict.loads(str(file.read()))
                        return data[string_id]
                except KeyError:
                    print(f"| Xyn/localization | \"{string_id}\" also isn't available in en-us!!")
                    return None

# Example for easy debugging
if __name__ == "__main__":
    print(internal.read("uwu","pt-br"))

#class external:
    #def read(string_id,lang="en-us"):
