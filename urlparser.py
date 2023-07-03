import requests

downloadpath = "C:/GIL/Down/"
with open("./downloadpath.txt", "r") as f:
    downloadpath = f.read()


# downloads an image by link, saves to path as filename
def download(link, path, filename, **kwargs):
    with open(path + filename, "wb") as img_file:
        img_file.write(requests.get(link, **kwargs).content)


# generic url cleaner
def cleanurl(url: str):
    return url.split("?")[0]




