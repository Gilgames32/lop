from enum import Enum
from discord import Embed
from discord.utils import escape_markdown

from util.urlparser import download, downloadembed


class PostType(Enum):
    TEXT = 1
    IMAGE = 2
    GALLERY = 3
    VIDEO = 4
    POLL = 5
    CROSSPOST = 6
    UNKNOWN = 7


class Post:
    _prefix = ""
    _platform = "unknown"

    def __init__(self, url: str):
        # common
        self._url = url
        self._author = None
        self._author_icon = None
        self._title = None
        self._type = None
        self._id = None
        # date maybe?
        
        self._fetched = False

        # text
        self._text = None

        # image
        self._media = []

        # video
        self._thumbnail = None

        # poll
        self._poll = None

        # crosspost
        self._parent = None

    async def fetch(self):
        self._fetched = True
    
    def webhook_avatar(self) -> str:
        return self._author_icon

    def webhook_username(self) -> str:
        return self._prefix + self._author

    def webhook_message(self, include_author = False, markdown = False) -> str:
        if not self._fetched:
            raise Exception("The post was not fetched")

        # title
        if self._title:
            message = f"**{self._title if markdown else escape_markdown(self._title)}**\n\n"
        else:
            message = ""

        # text
        if self._text:
            message += f"{self._text if markdown else escape_markdown(self._text)}\n"
            if not self._title:
                message += "\n"

        # footer
        message += f"-# Posted "
        if include_author:
            message += f"by {self._prefix}{self._author if markdown else escape_markdown(self._author)} "
        message += f"on [{self._platform}](<{self._url}>) "

        # media
        match self._type:
            case PostType.TEXT:
                pass
            case PostType.IMAGE:
                message += f"[.]({self._media[0]})"
            case PostType.GALLERY:
                for url in self._media:
                    message += f"[.]({url}) "
            case PostType.VIDEO:
                message += f"[.]({self._media[0]})"
            case PostType.POLL:
                raise Exception("Polls are not supported yet")
            case PostType.CROSSPOST:
                raise Exception("Crossposts are not supported yet")

        if len(message) > 2000:
            message = " ".join(message[:1997].split(" ")[:-1]) + "..." # profound mental retardation
        return message
    
    def download(self, path: str) -> Embed:
        if not self._fetched:
            raise Exception("The post was not fetched")
        if self._type not in [PostType.IMAGE, PostType.VIDEO, PostType.GALLERY]:
            raise Exception("This post is not downloadable")
        
        # download media
        if self._type == PostType.GALLERY:
            for i, url in enumerate(self._media):
                ext = url.split('.')[-1].split('?')[0]
                filename = f"{self._author}_{self._id}_{i}.{ext}"
                download(url, path, filename)
        else:
            url = self._media[0]
            ext = url.split('.')[-1].split('?')[0]
            filename = f"{self._author}_{self._id}.{ext}"
            download(url, path, filename)

        thumbnail = self._thumbnail if self._type == PostType.VIDEO else self._media[0]
        return downloadembed(self._url, thumbnail, filename)
        


class Poll:
    def __init__(self):
        self._title = None
        self._options = [] # stored in tuples (option, votes)
        self._total_votes = 0