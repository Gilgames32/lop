import json
import os


# save jsons
def savejson(jsonname: str, jdata):
    with open(f"{jsonname}.json", "w+") as outpoot:
        json.dump(jdata, outpoot, sort_keys=True, indent=4)


# load jsons
def loadjson(jsonname: str):
    with open(f"{jsonname}.json", "r") as inpoot:
        return json.load(inpoot)
    

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