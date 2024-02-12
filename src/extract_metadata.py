import os
import yaml

with open("credentials.yml", "r") as file:
    credentials = yaml.safe_load(file)


def sort_insta_posts(data_path: str) -> dict:
    """sorts downloaded instagram files by filtering for only text and images,
    and saves them in a dictionary according to each individual posts which are determined by the date and time posted.

    Args:
        data_path (str): filepath of the instagram posts

    Returns:
        dict: dictionary of sorted instagram posts
    """
    posts_dict = {}
    file_format_tuple = ("jpg", "jpeg", "png", "txt")
    files = os.listdir(data_path)
    for f in files:
        if f.lower().endswith(file_format_tuple):
            f_name = f.split("_UTC")[0]
            if f_name not in posts_dict:
                posts_dict[f_name] = [f]
            else:
                posts_dict[f_name].append(f)
        else:
            pass
    return posts_dict


def extract_metadata(posts_dict: dict):
    """Rearranges list of files from each post to have the text file to be the first element. Extracts metadata from text files, and uses some of the metadata for the images from the same post.
    Images metadata include post_id, cuisine, location, while text metadata include additional fields such as price, taste, worth-it,

    Args:
        posts_dict (dict): metadata dictionary for the texts and images.
    """
    all_metadata_dict = {}
    for post, files_list in posts_dict.items():
        # rearrange text file to be first element in list so that metadata of text can be extracted first
        text_file_index = files_list.index(f"{post}_UTC.txt")
        files_list.insert(0, files_list.pop(text_file_index))
        # extract and populate text metadata

        # fill up images metadata as first element is text
        for file in files_list[1:]:
            file_metadata_dict = {}
            file_metadata_dict["post_id"] = post


if __name__ == "__main__":
    posts_dict = sort_insta_posts(f"./data/{credentials['USERNAME']}")
    extract_metadata(posts_dict=posts_dict)
