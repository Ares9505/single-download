import os
import logging
from typing import List, Tuple, Optional
from datetime import datetime as dt

import asyncio
import pyrogram
import yaml
import json
import jsonpickle


from utils.file_management import get_next_name, manage_duplicate_file
from utils.log import LogFilter
from utils.meta import print_meta


logging.basicConfig(level=logging.INFO)
# logging.getLogger("pyrogram.session.session").addFilter(LogFilter())
# logging.getLogger("pyrogram.client").addFilter(LogFilter())
logger = logging.getLogger("media_downloader")



FAILED_IDS: list = []

def check_audio(message: dict):
    try:
        audio = message.audio
        print(type(message.audio))
        return True
    except:
        return False

def split_list(seq):
    os.makedirs('splited_json', exist_ok=True)
    avg = len(seq) / 1
    out = []
    last = 0.0
    count = 0

    while last < len(seq):

        result = seq[int(last):int(last + avg)]
        json.dump(result, open('splited_json/{}.json'.format(count), 'w'), indent=4)
        count = count + 1
        last += avg  
    # last_list_message=json.loads(result[9]) # result es una lista de strings q contiene json pra guardar en splited/json
    # # se quiere escoger el ultimo id del ultimo json del de la lista de strings 
    # out = last_list_message["py/state"]["message_id"] #ultimo id
    return out 



def update_config(config: dict):

    config["ids_to_retry"] = list(set(config["ids_to_retry"] + FAILED_IDS))
    with open("config.yaml", "w") as yaml_file:
        yaml.dump(config, yaml_file, default_flow_style=False)


async def begin_import(config: dict, pagination_limit: int) -> dict:

    client = pyrogram.Client(
        "media_downloader",
        api_id = 8138563,
        api_hash = "ae1b0ed21810912df1a6280c5bd016b5",
    )
    pyrogram.session.Session.notice_displayed = True
    await client.start()
    last_read_message_id: int = config["last_read_message_id"]

    messages_iter = client.iter_history(
        "spotify_down_bot",
        reverse=True,
    )
    pagination_count: int = 0
    messages_list: list = []

    async for message in messages_iter:
        if check_audio(message):
            print(message.message_id)
            message = jsonpickle.encode(message)
            if pagination_count != pagination_limit:
                pagination_count += 1
                messages_list.append(message)
            else:
                pagination_count = 0
                messages_list.append(message)

        else:
            pass

        print(len(messages_list))

        if len(messages_list) == 100:
                await client.stop()
                split_list(messages_list)
                # storaging last message_id
                last_message_list = json.loads(messages_list[99])              
                last_read_message_id = last_message_list["py/state"]["message_id"]
                print(last_read_message_id)
                config["last_read_message_id"] = last_read_message_id  

                return config

    await client.stop()
    last_read_message_id = split_list(messages_list)
    config["last_read_message_id"] = last_read_message_id
    return config

def main():
    """Main function of the downloader."""
    f = open("config.yaml")
    config =yaml.safe_load(f)
    f.close()
    updated_config = asyncio.get_event_loop().run_until_complete(
        begin_import(config, pagination_limit=100)
    )
    update_config(updated_config)


if __name__ == "__main__":
    print_meta(logger)
    main()
