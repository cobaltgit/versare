# Versare Rewrite

The rewrite branch of Versare, the in-development versatile(?) Discord bot

## Setup Instructions

### System Requirements
* Git is required to fetch the repository code
* Python 3.10 and pipenv is required to install dependencies
* ffmpeg is required for the youtube-dl command to work
* PostgreSQL's `psql` command-line utility is recommended to connect to the database from the command line

Install these with your system package manager

### Fetching the code

To fetch the code, you need to have git installed on your machine.  
Run the following command in a directory on your computer to clone the repository
```bash
$ git clone https://github.com/cobaltgit/versare.git
```

### Installing dependencies

Create a virtual environment and install dependencies from pip
```bash
$ pipenv install
```

#### Development dependencies

To set up development tools, run the following command
```bash
$ pipenv install --dev
...
$ pre-commit install
```

### Running the bot

#### Authenticating with Discord

In order to run the bot, you must obtain a Discord bot token - Instructions are [here](https://discordpy.readthedocs.io/en/stable/discord.html)*  
Rename `config.example.yml` to `config.yml` and paste your token into the `auth` section

*To enable slash commands (required from April-May 2022 for bots above 76 servers), also tick the `applications.commands` scope

#### Setting up Postgres

Ensure you have a PostgreSQL server running for your database  
Enter the database name, username, password, IP address and port of your PostgreSQL server into the `postgres` section of your config.yml

#### Setting up Lavalink

A Lavalink setup is required for the music cog to work.
Follow [these instructions](https://github.com/freyacodes/Lavalink#server-configuration) to set up a Lavalink node

Enter your node details into the `lavalink` section of your config.yml
```yml
lavalink:
    host: localhost # localhost if you're setting up your own on the same machine, otherwise use the WAN-facing IP of your node if on a separate machine from LAN
    port: 2333 # defaults to 2333 on server application.yml file - typically use 443 when connecting to an SSL-enabled node
    password: youshallnotpass # the password for the node, defaults to youshallnotpass on server application.yml file
    https: ["true", "false"] # specify whether to use a secure websocket connection to the node - either true or false
    identifier: MAIN # optional parameter - defaults to MAIN - the identifier of the node
```

#### (Optional) GitHub API Token

For the Discord token invalidator to work, copy and paste a GitHub personal access token into the `auth` section of your config.yml  
This is a completely optional step and doesn't affect the bot itself  
It's recommended that you use a separate, unused GitHub account for this operation.

#### Launching

Assuming you've followed the above instructions, you should be able to launch your bot.
```
$ pipenv run start
Versare is online - logged in as YourBotName#1234
Client ID: your bot's client ID
Prefix: v.
```

Congratulations! You've launched your own instance of Versare!

## CONTRIBUTIONS

The Versare project is welcome for contributions!  
Feel free to fork and submit pull requests to the repository at any time!

### Requirements
* You'll need to have the [system requirements](https://github.com/cobaltgit/versare#setup-instructions) installed on your machine
* Fetch the code and install the base dependencies and development tools - instructions [here](https://github.com/cobaltgit/versare#installing-dependencies)
* Have a development-ready text editor at hand (VSCode recommended)
* It's also recommended to run a private instance for testing
