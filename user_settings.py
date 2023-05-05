from objdict import ObjDict
import objdict
import os
import discord

def new_user(id):
    data = ObjDict()
    if not os.path.isdir("./user_data"):
        os.makedirs("./user_data")
    f = open(f"./user_data/{id}.json","w")
    f.write(objdict.dumps(data))
    f.close()

def set(id,option,value):
    if not os.path.isdir("./user_data"):
        os.makedirs("./user_data")
    if not os.path.exists(f"./user_data/{id}.json"):
        new_user(id)
        data = ObjDict()
    else:
        with open(f"./user_data/{id}.json","r") as user_data:
            try:
                data = objdict.loads(str(user_data.read()))
            except objdict.JsonDecodeError:
                new_user(id)
                with open(f"./user_data/{id}.json","r") as user_data:
                    data = objdict.loads(str(user_data.read()))
    data[option] = value
    with open(f"./user_data/{id}.json","w") as user_data:
        user_data.write(objdict.dumps(data))

def read(id,option,default=None):
    try:
        with open(f"./user_data/{id}.json","r") as user_data:
            data = objdict.loads(str(user_data.read()))
            try:
                return data[option]
            except KeyError:
                if default == None:
                    return Exception(f"The guild ({id}) does not contain '{option}' stored in it's settings!")
                else:
                    set(id,option,default)
                    return default
    except FileNotFoundError:
        new_user(id=id)
    
def remove(id,option):
    if not os.path.isdir("./user_data"):
        os.makedirs("./user_data")
    if not os.path.exists(f"./user_data/{id}.json"):
        raise Exception("There's no data for this guild!")
    with open(f"./user_data/{id}.json","r") as user_data:
        data = objdict.loads(str(user_data.read()))
    with open(f"./user_data/{id}.json","w") as user_data:
        try:
            del data[option]
            user_data.write(objdict.dumps(data))
        except KeyError:
            pass