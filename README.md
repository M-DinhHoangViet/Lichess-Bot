# Overview

**Lichess-Bot** is a bot for Lichess. It connects any [UCI](https://backscattering.de/chess/uci/) engine with the [Lichess Bot API](https://lichess.org/api#tag/Bot).

It has a customizable support of Polyglot opening books, a variety of supported online opening books and an online endgame tablebase. It can query local Syzygy and Gaviota endgame tablebases.

In addition, Lichess-Bot can autonomously challenge other bots in any variants. It optionally supports two separate engines, one for standard chess and chess960 and one for Lichess chess variants.

# How to install

- **NOTE: Only Python 3.10 or later is supported!**
- Download the repo into Lichess-Bot directory: `https://github.com/M-DinhHoangViet/Lichess-Bot.git`
- Navigate to the directory in cmd/Terminal: `cd Lichess-Bot`

Install all requirements:
```bash
python -m pip install -r requirements.txt
```

- Customize the `config.yml` according to your needs.

## Lichess OAuth
- Create an account for your bot on [Lichess.org](https://lichess.org/signup).
- **NOTE: If you have previously played games on an existing account, you will not be able to use it as a bot account.**
- Once your account has been created and you are logged in, [create a personal OAuth2 token with the "Play games with the bot API" ('bot:play') scope](https://lichess.org/account/oauth/token/create?scopes[]=bot:play&description=Lichess-Bot) selected and a description added.
- A `token` will be displayed. Store this in the `config.yml` file as the `token` field.
- **NOTE: You won't see this token again on Lichess, so do save it.**

## Setup Engine
Within the file `config.yml`:
- Enter the directory containing the engine executable in the `engine: dir` field.
- Enter the executable name in the `engine: name` field.
- You need to adjust the settings in `engine: uci_options` depending on your system.

## Setup opening book
To use an opening book, you have to enter a name of your choice and the path to the book at the end of the config in the `books` section.

In the upper `engine: opening_books: books` section you only have to enter the name you just chose. In addition, different books can be used for white, black and chess960. If no specific book is defined, the `standard` books are used.

For example, the `books` section could look like this:
```yaml
books:
  Goi: "./engines/Goi.bin"
  Perfect: "/home/Books/Perfect2021.bin"
  Cerebellum: "Cerebellum.bin"
```
A corresponding `engine: opening_books:` section could look like this:
```yaml
  opening_books:
    enabled: true
    books:
      white:
        - "Perfect"
        - "Goi"
#     black:
#       - "BlackBook"
      standard:
        - "Cerebellum" 
#     chess960:
#       - "Chess960Book"
    selection: "weighted_random"
```

# How to control

## Interactive mode

In this mode the bot is controlled by commands entered into the console.

### Start

To start the bot, type:

```bash
python user_interface.py
```
The bot automatically accepts challenges. Which challenges are accepted is defined in the config in the section `challenge`.

To see all commands, type:
```
help
```

### Matchmaking

To challenge other players with similar ratings, type:
```
matchmaking
```

Change the settings in `matchmaking` in the config to change how this bot challenges other players. The bot will pause matchmaking for incoming challenges. To exit the matchmaking mode type:
```
stop
```

To exit the bot completely, type:
```
quit
```

The bot will always wait until the current game is finished.

## Non interactive mode

This mode is used automatically when Lichess-Bot is used without an interactive terminal, for example as a service. In this case, the bot is controlled by setting flags at start time.

### Matchmaking

To let the bot challenge other bots in non interactive mode, start it like this:

```bash
python user_interface.py --matchmaking
```

**CAUTION**: Lichess will rate limit you if you let matchmaking run too long without adjusting the delay accordingly.

## Upgrade to Bot account

When the bot is running in interactive mode it will ask for an account upgrade if necessary.

In non interactive mode the `--upgrade` flag must be set at start.


```bash
python user_interface.py --upgrade
```

The account **cannot have played any game** before becoming a Bot account. The upgrade is **irreversible**. The account will only be able to play as a Bot.

## Running with Docker

The project comes with a Dockerfile, this uses Ubuntu 22.04, installs all dependencies, downloads the latest version of Stockfish and starts the bot.

If Docker is used, all configurations must be done in `config.yml.default`. This is automatically renamed to `config.yml` in the build process.

The Dockerfile also contains all commands to download Fairy-Stockfish and all NNUEs needed for the Lichess chess variants. These commands must be uncommented if desired. In addition, the variants engine must be enabled in the `config.yml`. To use NNUE for the Lichess chess variants the following UCI option for Fairy-Stockfish must be set in the config: `EvalFile: "3check-313cc226a173.nnue:antichess-689c016df8e0.nnue:atomic-2cf13ff256cc.nnue:crazyhouse-8ebf84784ad2.nnue:horde-28173ddccabe.nnue:kingofthehill-978b86d0e6a4.nnue:racingkings-636b95f085e3.nnue"`

If the service should run with matchmaking the `--matchmaking` flag must be appended at the end of the `ExecStart` line.

**Note**: If you want the bot to run in matchmaking mode for a long time, it is recommended to set the `matchmaking` `delay` higher to avoid problems with the Lichess rate limit. I recommend the following formula: `delay = 430 - 2 * initial_time - 160 * increment`

## Acknowledgements
Thanks to the Lichess team, especially T. Alexander Lystad and Thibault Duplessis for working with the LeelaChessZero team to get this API up. Thanks to the [Torom](https://github.com/Torom)made to [Torom/BotLi](https://github.com/Torom/BotLi) is original. Thanks to the [Niklas Fiekas](https://github.com/niklasf) and his [python-chess](https://github.com/niklasf/python-chess) code which allows engine communication seamlessly. In addition, the idea of this bot is based on [ShailChoksi/lichess-bot](https://github.com/ShailChoksi/lichess-bot).

## License
**LichessBOT-Việt** is licensed under the AGPLv3 (or any later version at your option). Check out the [LICENSE file](/LICENSE) for the full text.
