import asyncio
import os
import re
import time
from typing import List
from PIL import Image
import matplotlib.pyplot as plt
import yaml

from conf import conf
from logs.logging import logger

with open("credentials.yml", "r") as file:
    credentials = yaml.safe_load(file)
USERNAME = credentials["USERNAME"]


def filter_relevant_images(image_uri: list, distances: list) -> List[tuple]:
    """Given a list of retrieved images queried from the image collection, further filter the list
     to get the most relevant images based on distance similarity.

    Args:
        image_uri (list): list of image uris
        distances (list): list of image distance similarity

    Returns:
        List[tuple]: List of the most relevant images and their respective distance similarity
    """
    threshold = distances[0] * conf["image_relevance_threshold"]
    filtered_images = [
        (doc_id, dist)
        for doc_id, dist in zip(image_uri, distances)
        if dist <= threshold
    ]
    return filtered_images


def parse_response(response: str) -> str:
    """remove thinking tokens and extract the final answer from the llm when using reasoning models
    like deepseek.

    Args:
        response (str): llm response that may contain thinking tokens

    Returns:
        str: final answer
    """
    return re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL).strip()


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


def plot_images(image_paths: List[str]):
    images_shown = 0
    plt.figure(figsize=(16, 9))
    for img_path in image_paths:
        if os.path.isfile(img_path):
            image = Image.open(img_path)

            plt.subplot(2, 3, images_shown + 1)
            plt.imshow(image)
            plt.xticks([])
            plt.yticks([])

            images_shown += 1
            if images_shown >= 9:
                break
    plt.show()
