from objdict import ObjDict
import objdict
import os
import shutil

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
        with open(f"./users/{id}.json","r") as file:
            data = objdict.loads(str(file.read()))
            try:
                return data[option]
            except KeyError:
                return None