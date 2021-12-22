# Versare Rewrite

The rewrite branch of Versare, the in-development versatile(?) Discord bot

## Setup Instructions

### System Requirements
* Git is required to fetch the repository code
* Python 3.10 and pip is required with the virtualenv module

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
$ python3 -m venv venv
$ source venv/bin/activate
(venv) $ pip install -r requirements.txt
```

To install development tools, run the following command
```bash
(venv) $ pip install -r requirements-dev.txt
```

### Running the bot

#### Authenticating with Discord

In order to run the bot, you must obtain a Discord bot token - Instructions are [here](https://discordpy.readthedocs.io/en/stable/discord.html)*  
Rename `config.example.yml` to `config.yml` and paste your token into the `auth` section

*To enable slash commands, also tick the `applications.commands` scope

#### Setting up Postgres

Ensure you have a PostgreSQL server running for your database  
Enter the database name, username, password, IP address and port of your PostgreSQL server into the `postgres` section of your config.yml

#### Launching

Assuming you've followed the above instructions, you should be able to launch your bot.
```
(venv) $ python3 runner.py
Versare is online - logged in as YourBotName#1234
Client ID: your bot's client ID
Prefix: v.
```

Congratulations! You've launched your own instance of Versare!
