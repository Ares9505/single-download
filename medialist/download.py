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
logging.getLogger("pyrogram.session.session").addFilter(LogFilter())
logging.getLogger("pyrogram.client").addFilter(LogFilter())
logger = logging.getLogger("media_downloader")

FAILED_IDS: list = []


try:
    file_path = load(open("download_path.json", 'r'))
    THIS_DIR = file_path['path']
except:
    THIS_DIR = os.path.dirname(os.path.abspath("."))


def update_config(config: dict):

    config["ids_to_retry"] = list(set(config["ids_to_retry"] + FAILED_IDS))
    with open("config.yaml", "w") as yaml_file:
        yaml.dump(config, yaml_file, default_flow_style=False)


def _can_download(
        _type: str, file_formats: dict, file_format: Optional[str]) -> bool:

    if _type in ["audio"]:
        allowed_formats: list = file_formats[_type]
        if not file_format in allowed_formats and allowed_formats[0] != "all":
            return False
    return True


def _is_exist(file_path: str) -> bool:
    return not os.path.isdir(file_path) and os.path.exists(file_path)


def _get_media_meta(media_obj: pyrogram.types.messages_and_media, _type: str) -> Tuple[str, Optional[str]]:
    if _type in ["audio"]:
        # if _type in ["audio", "document", "video"]:
        file_format: Optional[str] = media_obj.mime_type.split("/")[-1]
    else:
        file_format = None

    if _type == "voice":
        file_format = media_obj.mime_type.split("/")[-1]
        file_name: str = os.path.join(
            THIS_DIR,
            _type,
            "voice_{}.{}".format(
                dt.utcfromtimestamp(media_obj.date).isoformat(), file_format
            ),
        )
    else:
        file_name = os.path.join(
            THIS_DIR, _type, getattr(media_obj, "file_name", None) or ""
        )
    return file_name, file_format


def download_media(
        client: pyrogram.client.Client,
        message: pyrogram.types.Message,
        media_types: List[str],
        file_formats: dict,
):
    for retry in range(3):
        try:
            print(message.message_id)
            if message.media is None:
                
                return message.message_id
            for _type in media_types:
                _media = getattr(message, _type, None)
                if _media is None:
                    continue
                file_name, file_format = _get_media_meta(_media, _type)
                if _can_download(_type, file_formats, file_format):
                    if _is_exist(file_name):
                        file_name = get_next_name(file_name)
                        print("intentando descarga")
                        download_path = client.download_media(
                            message, file_name=file_name
                        )
                        download_path = manage_duplicate_file(download_path)

                    else:

                        download_path = client.download_media(
                            message, file_name=file_name
                        )
                    if download_path:
                        logger.info("Media downloaded - %s", download_path)
            break
        except pyrogram.errors.exceptions.bad_request_400.BadRequest:
            logger.warning(
                "Message[%d]: file reference expired, refetching...",
                message.message_id,
            )
            message = client.get_messages(
                chat_id=message.chat.id,
                message_ids=message.message_id,
            )
            if retry == 2:
                # pylint: disable = C0301
                logger.error(
                    "Message[%d]: file reference expired for 3 retries, download skipped.",
                    message.message_id,
                )
                FAILED_IDS.append(message.message_id)
        except TypeError:
            # pylint: disable = C0301
            logger.warning(
                "Timeout Error occured when downloading Message[%d], retrying after 5 seconds",
                message.message_id,
            )
            if retry == 2:
                logger.error(
                    "Message[%d]: Timing out after 3 reties, download skipped.",
                    message.message_id,
                )
                FAILED_IDS.append(message.message_id)
        except Exception as e:
            # pylint: disable = C0301
            logger.error(
                "Message[%d]: could not be downloaded due to following exception:\n[%s].",
                message.message_id,
                e,
                exc_info=True,
            )
            FAILED_IDS.append(message.message_id)
            break
    return message.message_id

def process_messages(
        client: pyrogram.client.Client,
        messages: List[pyrogram.types.Message],
        media_types: List[str],
        file_formats: dict,
) -> int:
    message_ids = [
            download_media(client, message, media_types, file_formats)
            for message in messages
        ]


    last_message_id = max(message_ids)
    return last_message_id

def begin_import(config: dict, pagination_limit: int, messages_list: list) -> dict:
    client = pyrogram.Client(
        "media_downloader",
        api_id = 8138563,
        api_hash= "ae1b0ed21810912df1a6280c5bd016b5",
    )
    pyrogram.session.Session.notice_displayed = True
    client.start()
    last_read_message_id: int = config["last_read_message_id"]

    if messages_list:
        last_read_message_id = process_messages(
            client,
            messages_list,
            config["media_types"],
            config["file_formats"],
        )

    client.stop()
    config["last_read_message_id"] = last_read_message_id
    return config


def main():
    """Main function of the downloader."""
    f = open("config.yaml")
    config = yaml.safe_load(f)
    f.close()
    file_list = json.load(open('messages.json', 'r'))

    list_messages = [jsonpickle.decode(message) for message in file_list]
    updated_config = begin_import(config, pagination_limit=100, messages_list=list_messages)
    # update_config(updated_config)


if __name__ == "__main__":
    print_meta(logger)
    main()
