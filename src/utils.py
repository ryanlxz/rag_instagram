import asyncio
import os
import time

import yaml

from conf import conf
from logs.logging import logger

with open("credentials.yml", "r") as file:
    credentials = yaml.safe_load(file)
USERNAME = credentials["USERNAME"]


def count_files_in_folder(folder_path):
    """Counts the number of files in the given folder."""
    return len(
        [
            f
            for f in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, f))
        ]
    )


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
