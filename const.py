import os
import json
import discord
from dotenv import load_dotenv


# save jsons
def savejson(jsonname: str, jdata):
    with open(f"{jsonname}.json", "w+") as outpoot:
        json.dump(jdata, outpoot, sort_keys=True, indent=4)


# load jsons
def loadjson(jsonname: str):
    with open(f"{jsonname}.json", "r") as inpoot:
        return json.load(inpoot)
    

# create conf if it doesnt exist
if not os.path.exists("./conf.json"):
    conf = {
        "debug": False,
        "reddit_token_birth": 0,
        "dev": 954419840251199579,
        "labowor": 834100481839726693,
        "tostash": 1113025678632300605,
        "tomarkdown": 969498055151865907,
        "tomarkdown_debug": 1012384595611746465
    }
    savejson("conf", conf)
    print("conf.json was created")


# init
load_dotenv()
# debug
conf = loadjson("conf")
LOPDEBUG = conf["debug"]

# ids
dev = conf["dev"]
labowor = discord.Object(id=conf["labowor"])
tostash_chid = conf["tostash"]
tomarkdown_chid = conf["tomarkdown"]
# tokens
webhookurl = os.getenv("WEBHOOK32")
# debug channel overwrites
if LOPDEBUG:
    # instead of #floof it will listen to #test
    webhookurl = os.getenv("WEBHOOK_DEBUG")
    tomarkdown_chid = conf["tomarkdown_debug"]