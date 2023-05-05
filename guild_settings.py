from objdict import ObjDict
import objdict
import os

def new_guild(id):
    data = ObjDict()
    if not os.path.isdir("./guild_data"):
        os.makedirs("./guild_data")
    f = open(f"./guild_data/{id}.json","w")
    f.write(objdict.dumps(data))
    f.close()

def set(id,option,value):
    if not os.path.isdir("./guild_data"):
        os.makedirs("./guild_data")
    if not os.path.exists(f"./guild_data/{id}.json"):
        new_guild(id)
        data = ObjDict()
    else:
        with open(f"./guild_data/{id}.json","r") as guild_data:
            try:
                data = objdict.loads(str(guild_data.read()))
            except objdict.JsonDecodeError:
                new_guild(id)
                with open(f"./guild_data/{id}.json","r") as guild_data:
                    data = objdict.loads(str(guild_data.read()))
    data[option] = value
    with open(f"./guild_data/{id}.json","w") as guild_data:
        guild_data.write(objdict.dumps(data))

def read(id,option,default=None):
    try:
        with open(f"./guild_data/{id}.json","r") as guild_data:
            data = objdict.loads(str(guild_data.read()))
            try:
                return data[option]
            except KeyError:
                if default == None:
                    return Exception(f"The guild ({id}) does not contain '{option}' stored in it's settings!")
                else:
                    set(id,option,default)
                    return default
    except FileNotFoundError:
        new_guild(id=id)
    
def remove(id,option):
    if not os.path.isdir("./guild_data"):
        os.makedirs("./guild_data")
    if not os.path.exists(f"./guild_data/{id}.json"):
        raise Exception("There's no data for this guild!")
    with open(f"./guild_data/{id}.json","r") as guild_data:
        data = objdict.loads(str(guild_data.read()))
    with open(f"./guild_data/{id}.json","w") as guild_data:
        try:
            del data[option]
            guild_data.write(objdict.dumps(data))
        except KeyError:
            pass
