from objdict import ObjDict
import objdict
import os
import shutil

class user:
    def set(id,option,value):
        #Check if it exists
        if not os.path.isdir("./users/"):
            os.makedirs("./users/")
        if not os.path.exists(f"./users/{id}.json"):
            data = ObjDict()
        else:
            with open(f"./users/{id}.json","r") as file:
                try:
                    data = objdict.loads(str(file.read()))
                except objdict.JsonDecodeError:
                    print(f"Data for the user {id} is broken -_-")
                    shutil.move(f"./users/{id}.json",f"./users/{id}_backup.json")   #Don't wanna lose user data UwU
                    
                data = ObjDict()
                file.close()
            
        with open(f"./users/{id}.json","w") as file:
            data[option] = value 
            file.write(objdict.dumps(data))
            file.close()

    def read(id,option):
        if not os.path.isdir("./users/"):
            os.makedirs("./users/")
        if not os.path.exists(f"./users/{id}.json"):
            return None
        else:
            try:
                with open(f"./users/{id}.json","r") as file:
                    data = objdict.loads(str(file.read()))
                try:
                    return data[option]
                except KeyError:
                    return None
            except:
                return None

    def remove(id,option):
        if not os.path.isdir("./users/"):
            os.makedirs("./users/")
        if not os.path.exists(f"./users/{id}.json"):
            return None
        else:
            try:
                with open(f"./users/{id}.json","r") as file:
                    data = objdict.loads(str(file.read()))
                    del data[option]
                    file.write(objdict.dumps(data))
                    file.close()
            except:
                return None
                

class guild:
    def set(id,option,value):
        #Check if it exists
        if not os.path.isdir("./guilds/"):
            os.makedirs("./guilds/")
        if not os.path.exists(f"./guilds/{id}.json"):
            data = ObjDict()
        else:
            with open(f"./guilds/{id}.json","r") as file:
                try:
                    data = objdict.loads(str(file.read()))
                except objdict.JsonDecodeError:
                    print(f"Data for the guild {id} is broken -_-")
                    shutil.move(f"./guilds/{id}.json",f"./guild/{id}_backup.json")   #Don't wanna lose user data UwU
                    data = ObjDict()
                    file.close()
            
        with open(f"./guilds/{id}.json","w") as file:
            data[option] = value 
            file.write(objdict.dumps(data))
            file.close()

    def read(id,option):
        if not os.path.isdir("./guilds/"):
            os.makedirs("./guilds/")
        if not os.path.exists(f"./guilds/{id}.json"):
            return None
        else:
            with open(f"./guilds/{id}.json","r") as file:
                data = objdict.loads(str(file.read()))
                try:
                    return data[option]
                except KeyError:
                    return None
                
    def remove(id,option):
        if not os.path.isdir("./guilds/"):
            os.makedirs("./guilds/")
        if not os.path.exists(f"./guilds/{id}.json"):
            return None
        else:
            try:
                with open(f"./guilds/{id}.json","r") as file:
                    data = objdict.loads(str(file.read()))
                    del data[option]
                    file.write(objdict.dumps(data))
                    file.close()
                    return True
            except:
                return None