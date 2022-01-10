# Versare

A general-purpose **WORK-IN-PROGRESS - INCOMPLETE** Discord bot for the masses  
The public instance is currently unavailable, please follow the instructions to set up your own

## NOTE: VERSARE IS MOVING TO HIKARI

### Requirements

This is what you'll need to run your bot:  
```
GCC
Python 3.9 installed on system - if you haven't already, use pyenv
SQLite3
Pipenv
```

Pip package requirements are below:  
```
enhanced-discord.py
wikipedia
lxml
jishaku
cryptography
asqlite
uvloop (on unix-like systems)
psutil
youtube-dl
thefuzz
python-Levenshtein
```

### TO-DO LIST
A list of things that need to be implemented next
* ADD MORE COMMANDS!!!
* Economy system
* Add mute system with timings
* Finish logging system
* Finish custom help command


## Setup

Instructions on how to set up your instance of Versare

### Fetching the code

To fetch the code, you need `git` installed on your system  
* Run this command in the terminal to clone the Git repository  
```bash
$ git clone https://github.com/cobaltgit/versare.git
```

### Installing the dependencies

Next, we need to install the dependencies so the code can run  
You'll need `pipenv` for this. If you don't have Python 3.9 installed on your system, use [`pyenv`](https://github.com/pyenv/pyenv).  
Follow the setup instructions from there and install 3.9(.9)  

* Assuming you've installed Python 3.9 properly if you haven't already, install `pipenv` with this command in the terminal
```bash
$ python3 -m pip install pipenv
```

* Install the required packages in your environment with this command:
```bash
$ pipenv install
```

#### OPTIONAL: DEV DEPENDENCIES
If you want to develop the bot further for yourself, it's recommended you install the dev dependencies for the git hooks
```bash
$ pipenv install --dev
$ pre-commit install
```

### Initialising the bot on Discord

Next, we'll need to initialise our bot on Discord's side   
* Click [this link](https://discord.com/developers/applications) to go to the Discord Developer Portal and log in if needed.  

* Click on the **New Application** button toward the top right corner and give a name to your instance (ideally Versare, but do whatver :) )  
* Go to the *Bot* tab on the sidebar and click **Add Bot**. This generates a new bot account on Discord's side.  
* Check all radio buttons under the **__Privileged Gateway Intents__** section.

### Authenticating the bot and launching

* Scroll up to the top, and click **Copy** underneath the *TOKEN* section.
* Also create a GitHub personal access token for the bot to use to invalidate tokens
* Create a file in the config directory with your favourite text editor.
```bash
$ nano config/auth.json
```
-> The file should look something like this:  
```json
{
    "token": "bot-token-here",
    "github_token": "github-token-here"
}
```
* Save the file and exit your editor.  
* Make sure only YOU can access the auth file:
```bash
$ chmod 600 config/auth.json
```

Finally, to launch your bot at any time, go to the directory containing the code and run this command:  
```bash
$ pipenv run start
```

### Inviting the bot to your server

* Go back to the developer portal and go to the *OAuth2* tab on the sidebar and the **__OAuth2 URL Generator__** section.  

* Tick the `bot` and `applications.commands` scopes under the *SCOPES* section and tick the `Administrator` permission underneath *BOT PERMISSIONS*  
  
* An invite link should appear underneath the *SCOPES* section. Copy that and paste it into a new browser tab, invite the bot to a server you own or moderate and Bob's your uncle. You've successfully set up an instance of Versare!

# CREDITS
[NextChai](https://github.com/NextChai) - [BaseButtonPaginator](https://github.com/cobaltgit/versare/tree/main/lib/views.py#L73-L207)
