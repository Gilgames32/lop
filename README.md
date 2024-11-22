# <img src="https://raw.githubusercontent.com/Gilgames32/lop/main/lop_pfp.png" width="128"> Lop#6400

[![Python application](https://github.com/Gilgames32/lop/actions/workflows/python-app.yml/badge.svg)](https://github.com/Gilgames32/lop/actions/workflows/python-app.yml) ![GitHub license](https://img.shields.io/github/license/Gilgames32/lop.svg)

An oddly specific Discord bot written in Python.

## Features

- Captioning media in the iFunny style, using [caption-redux](https://github.com/Gilgames32/caption-redux/)
- Better Twitter embeds, with no embeds
- Random animal pics using the [tinyfox api](https://tinyfox.dev/)
- Auto download art from specific channels
- Reverse image search using [SauceNAO](https://saucenao.com/)
- RSS feeds (WIP)

## Installation

> [!NOTE]
> This bot was made for personal use and is not meant to work across multiple servers as of now.

1. Clone this repository.
2. Install the required Python packages using pip:
    ```sh
    pip install -r requirements.txt
    ```
3. Add your tokens to the `.env` file in the root directory of this project.
    <details>
    <summary>Template</summary>
    
    ```env
    LOPTOKEN=your discord bot token
    SAUCETOKEN=your saucenao token, you monster
    WEBHOOK32=webhook link of the channel where embeds are replaced
    WEBHOOK_DEBUG=webhook link for debugging, or just use the latter
    REDDITCID=your reddit client id
    REDDITCSECRET=your reddit client secret
    ```

    </details>

4. Create a `conf.json` or run the bot once to have it created for you. Modify the contents of it based on your setup.
    <details>
    <summary>Template</summary>
    
    ```json
    {
        "debug": False, // for advanced users
        "reddit_token_birth": 0, // do not touch
        "dev": 954419840251199579, // your discord user id
        "labowor": 834100481839726693, // your server id
        "tostash": 1113025678632300605, // auto-download channel id
        "tomarkdown": 969498055151865907, // better embed channel
        "tomarkdown_debug": 1012384595611746465, // channel for testing
        "last_rss": 0, // do not touch
        "twfollows": [] // legacy
    }
    ```

    </details>


5. Run the bot
    ```sh
    python lop.pyw # or python3
    ```

6. Sync the command tree on Discord using `/sync`


## Contributing

Contributions are welcome! For more info reach out to me in the server below!

## Discord
[Server invite](https://discord.gg/X46A3CCZAE) to labowor
[Lop#6400](<https://discord.com/users/954628626463207464>) the bot
[gilgman](<https://discord.com/users/954419840251199579>) the developer
