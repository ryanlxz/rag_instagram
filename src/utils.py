import asyncio
import os
import time

import yaml

from conf import conf
from logs.logging import logger

with open("credentials.yml", "r") as file:
    credentials = yaml.safe_load(file)
USERNAME = credentials["USERNAME"]


def count_files_in_folder(folder_path: str) -> int:
    """Counts the number of files in the given folder.

    Args:
        folder_path (str): _description_

    Returns:
        int: number of files in the given folder
    """
    return len(
        [
            f
            for f in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, f))
        ]
    )


def count_text_files(folder_path: str) -> int:
    """Counts the number of text files in the given folder.

    Args:
        folder_path (str): folder path

    Returns:
        int: number of text files in the given folder
    """
    count = 0
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            count += 1
    return count


async def monitor_file_count():
    data_dir = f"{os.getcwd()}/data/{USERNAME}/"
    previous_count = count_files_in_folder(data_dir)
    start_time = time.time()

    while True:
        current_count = count_files_in_folder(data_dir)

        if (
            current_count == previous_count
            and (time.time() - start_time) > conf["monitor_file_count_interval"]
        ):
            logger.info(
                "No new files downloaded in the last minute. Stopping update_posts."
            )
            break

        previous_count = current_count
        await asyncio.sleep(conf["monitor_file_count_interval"])


def filter_pending_posts_for_update(
    sorted_posts_dict: dict, latest_vectordb_id: str
) -> dict:
    filtered_dict = {
        k: v for k, v in sorted_posts_dict.items() if k > latest_vectordb_id
    }
    return filtered_dict


test_dict = {
    "2024-09-27_16-54-51": 1,
    "2024-09-28_10-34-58": 2,
    "2024-09-30_13-48-48": 3,
}
latest_value = "2024-09-27_16-54-51"
filter_pending_posts_for_update(test_dict, latest_value)
