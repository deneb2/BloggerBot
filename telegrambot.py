import logging
import telepot
import logging
import logging.config
import yaml
import json

import utils

from exceptions import MetadataException


logging.config.fileConfig('config/logging.conf')
logger = logging.getLogger(__name__)

with open("config/config.yml", 'r') as stream:
    try:
        cfg = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

def log_message (level, text, data=None):
    """Utility function to log app behaviour"""
    json_obj = {
        "message": text,
        "data": data
    }
    logger.log(level, json.dumps(json_obj))


def main():
    """Script entry point

    flow:
    - get the messages from telegram
    - extract urls
    - dowload metadata
    - post data to wordpress
    """
    TelegramBot = telepot.Bot(cfg.get('TELEGRAM_TOKEN'))

    # last update_id saved to file
    try:
        with open('update_id') as f:
            last_update = int(f.readline())
    except:
        last_update = 0

    log_message(logging.DEBUG, 'new update id retreived',
                {'update_id': last_update})

    updates = TelegramBot.getUpdates(last_update+1)

    for up in updates:
        log_message(logging.DEBUG, 'got new message',
                    {'update': up})
        last_update = up['update_id']
        message = up.get('message')
        if message:
            text = message.get('text', '')
            date = message.get('date', '')
            author = message.get('from', {}).get('first_name', '')
            url = utils.extract_url(text)

            if url and cfg.get('WP_DOMAIN') not in url:
                metadata = utils.Metadata(cfg)

                try:
                    metadata.get_metadata(url)
                except MetadataException as e:
                    log_message(logging.WARNING, str(e), {"url": url})
                except Exception as e:
                    log_message(logging.ERROR, str(e), {"url": url})

                try:
                    utils.post_wordpress(cfg, date, author, metadata)
                except Exception as e:
                    log_message(logging.ERROR, str(e), {"url": url})

                log_message(logging.DEBUG, 'data published', metadata.to_json())

            else:
                log_message(logging.DEBUG, 'no urls in the message',
                            {'message': message})
        else:
            log_message(logging.DEBUG, 'no message info')

    with open('update_id', 'w') as f:
        f.write(str(last_update))
        log_message(logging.DEBUG, 'new update id stored',
                    {'update_id': last_update})
        f.close()

if __name__ == '__main__':
    main()

