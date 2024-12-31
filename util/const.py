import os
import json
from dotenv import load_dotenv


# save jsons
def savejson(jsonname: str, jdata):
    with open(f"{jsonname}", "w+") as outpoot:
        json.dump(jdata, outpoot, sort_keys=True, indent=4)


# load jsons
def loadjson(jsonname: str) -> dict:
    with open(f"{jsonname}", "r") as inpoot:
        return json.load(inpoot)

CONFPATH = "./conf.json"
conf = {}

def loadconf():
    global conf
    conf = loadjson(CONFPATH)

def saveconf():
    savejson(CONFPATH, conf)


# init
load_dotenv()

# load config
if not os.path.exists("./conf.json"):
    raise FileNotFoundError("conf.json not found")
loadconf()

LOPDEBUG = conf["debug"]
downloadpath = conf["downloadpath"]
dev = conf["dev"]
tostash_chid = conf["tostash"]

