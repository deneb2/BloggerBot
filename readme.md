# BloggerBot

This software is a Telegram bot. It will parse all the messages and it will post all the links to your blog wordpress.
This Bot need to be an _administrator_ of the group to read all the messages.

_**DISCLAIMER:**_ This is a just for fun project. There are no warranties on support or functionality.

## Prerequisite:
- a Telegram account and the API key.For the key ask the [@BotFather](https://telegram.me/botfather) or read the [documentation](https://telegram.org/blog/bot-revolution)
- a worpress blog: [how to install wordpress](https://wordpress.org/support/article/how-to-install-wordpress/)

## Installation:
- Clone this repository `git clone git@github.com:deneb2/BloggerBot.git`
- `cd BloggerBot/`
- Customize the configuration:
    - `cp config/config.yml.template config/config.yml`
    - `<your-editor> config/config.yml`
- Create and configure a virtual environment
    - `virtualenv -p python-3.8 env_bloggerbot`
    - `source env_bloggerbot/bin/activate`
    - `pip install -r requirements.txt`
- Start the script
    - `python telegrambot.py`
    - if you want to run the script continuously you can add a line in your crontab:
        - `*/5 * * * * python /path/to/script/telegrambot.py`
    - or test it on the shell
        - `watch -n 60 python telegrambot.py`

_PR/comments/fork are welcome_ 
