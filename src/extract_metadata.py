import os
from pathlib import Path
import yaml
from .extractor import Extractor
from typing import Tuple, List
import numpy as np
import json
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from logs.logging import logger

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

with open("credentials.yml", "r") as file:
    credentials = yaml.safe_load(file)


def sort_insta_posts(data_path: str) -> dict:
    """sorts downloaded instagram files by filtering for only text and images,
    and saves them in a dictionary according to each individual post which are determined by the date and time posted.
    Also handles reviews which are split into 2 or more separate posts. This is done by first checking if the post has a 'Taste' review, and if not,
    it will move on to the next post with a 'Taste' review. This assumes that the files are sorted in order, part 1, part 2.. etc of the review are posted back-to-back,
    and a post without a 'Taste' review is automatically classified as part 1 of a review.

    Args:
        data_path (str): directory path of the instagram posts

    Returns:
        dict: dictionary of sorted instagram posts
    """
    file_list = os.listdir(data_path)
    file_list = sorted(file_list)
    posts_dict = {}
    post_list = []
    for f in file_list:
        if f.lower().endswith("txt"):
            f_name = f.split("_UTC")[0]
            text = open_text_file(
                data_folder_path=Path(f"data/{credentials['USERNAME']}"), file_name=f
            )
            data_extractor = Extractor(text)
            taste = data_extractor.extract_taste()
            if not taste:
                post_list.extend(add_files_from_same_post(file_list, f_name))
            else:
                post_list.extend(add_files_from_same_post(file_list, f_name))
                posts_dict[f_name] = post_list
                post_list = []
    return posts_dict


def extract_metadata(
    posts_dict: dict,
) -> Tuple[List[str], List[dict], List[str], List[np.array], List[dict], List[str]]:
    """Separates list of files from each post into a text list and an image list.
    Extracts metadata from text files, and uses some of the metadata for the images from the same post.
    Images metadata include post_id, cuisine, location, while text metadata include additional fields such as price, taste, worth-it.

    Args:
        posts_dict (dict): Dictionary containing all the text and image files, sorted by each post as the keys.
    """
    (
        text_documents_list,
        text_metadata_list,
        text_id_list,
        image_documents_list,
        image_metadata_list,
        image_id_list,
        uri_list,
    ) = ([], [], [], [], [], [], [])
    for post, files_list in posts_dict.items():
        # extract and populate text metadata
        text_list, image_list = get_text_and_image_files(files_list)
        if len(text_list) > 1:
            text = combine_text_files(text_list)
        else:
            text = open_text_file(
                data_folder_path=Path(f"data/{credentials['USERNAME']}"),
                file_name=text_list[0],
            )
        text_documents_list.append(text)
        text_id_list.append(f"{post}_text")
        text_metadata_dict = extract_text_metadata(text)
        text_metadata_list.append(text_metadata_dict)

        # images
        cuisine = text_metadata_dict["cuisine"]
        location = text_metadata_dict["location"]
        data_folder_path = Path(f"data/{credentials['USERNAME']}")
        for num, image in enumerate(image_list):
            img = Image.open(Path(data_folder_path, image))
            uri_list.append(str(Path(data_folder_path, image)))
            img_array = np.array(img)
            image_documents_list.append(img_array)
            image_id_list.append(f"{post}_img_{num}")
            image_metadata_dict = {"cuisine": cuisine, "location": location}
            image_metadata_list.append(image_metadata_dict)
    return (
        text_documents_list,
        text_metadata_list,
        text_id_list,
        image_documents_list,
        image_metadata_list,
        image_id_list,
        uri_list,
    )

    # returns 3 lists
    # documents=["lorem ipsum...", "doc2", "doc3", ...],
    # metadatas=[{"chapter": "3", "verse": "16"}, {"chapter": "3", "verse": "5"}, {"chapter": "29", "verse": "11"}, ...],
    # ids=["id1", "id2", "id3", ...]


def extract_text_metadata(text: str) -> dict:
    data_extractor = Extractor(text)
    taste = data_extractor.extract_taste()
    cuisine = data_extractor.extract_cuisine()
    location = data_extractor.extract_location()
    text_metadata_dict = {"taste": taste, "cuisine": cuisine, "location": location}
    return text_metadata_dict


def open_text_file(data_folder_path: str, file_name: str) -> str:
    """helper function to open a text file

    Args:
        data_folder_path (str): folder path of the text file to be opened
        file_name (str): text filename

    Returns:
        str: text
    """
    # use encoding 'utf-8' for chinese characters
    text_file = open(Path(data_folder_path, file_name), "r", encoding="utf8")
    return text_file.read()


def add_files_from_same_post(file_list: list, post_prefix: str) -> list:
    """helper function which iterates through a list of file names, and returns all the files of relevant format with the same file name prefix

    Args:
        file_list (list): list of file names
        post_prefix (str): file name prefix

    Returns:
        list: list of file names with the same post_prefix
    """
    post_list = []
    file_format_tuple = ("jpg", "jpeg", "png", "txt")
    for f in file_list:
        if f.lower().endswith(file_format_tuple) and f.split("_UTC")[0] == post_prefix:
            post_list.append(f)
    return post_list


def get_text_and_image_files(files_list: list) -> Tuple[List[str], List[str]]:
    """helper function to sort the text and image files from a list of file names

    Args:
        files_list (list): list of file names

    Returns:
        Tuple[List[str], List[str]]: List[text file names], List[image file names]
    """
    text_list = []
    image_list = []
    for file in files_list:
        if file.lower().endswith("txt"):
            text_list.append(file)
        if file.lower().endswith(("jpg", "jpeg", "png")):
            image_list.append(file)
    return text_list, image_list


def combine_text_files(text_list: list) -> str:
    """helper function to combine text files into a single combined text

    Args:
        text_list (list): list of text file names

    Returns:
        str: combined text
    """
    combined_text = ""
    for file in text_list:
        combined_text += open_text_file(
            data_folder_path=Path(f"data/{credentials['USERNAME']}"), file_name=file
        )
    return combined_text


if __name__ == "__main__":
    folder_name = "eatinara_data"
    # posts_dict = sort_insta_posts(f"./data/{credentials['USERNAME']}")
