import csv
from datetime import datetime, timedelta
from itertools import dropwhile, takewhile
from pathlib import Path
import instaloader
import yaml
import os
from conf import conf
from logs.logging import logger

with open("credentials.yml", "r") as file:
    credentials = yaml.safe_load(file)


class GetInstagramProfile:
    def __init__(self) -> None:
        self.L = instaloader.Instaloader()
        self.L.login(credentials["USERNAME"], credentials["PASSWORD"])

    def download_users_profile_picture(self, username):
        self.L.download_profile(username, profile_pic_only=True)

    def download_posts(
        self, data_path: str, start_date: datetime, end_date: datetime, username: str
    ):
        """downloads posts from start_date to end_date into the data_path

        Args:
            data_path (str): folder path to save downloaded posts
            start_date (str): start date of posts to download
            end_date (str): end date of posts to download
            username (str): instagram username
        """
        posts = instaloader.Profile.from_username(self.L.context, username).get_posts()
        os.chdir(data_path)
        for post in takewhile(
            lambda p: p.date > start_date, dropwhile(lambda p: p.date > end_date, posts)
        ):
            logger.info(post.comments)
            self.L.download_post(post, username)
        logger.info(f"downloaded {username} posts")

    def download_user_posts(self, username: str):
        """Creates a new folder that is named as the Instagram Username, and downloads all the posts - text file, pictures in jpg, video in mp4.
        These files are named by the date posted.

        Args:
            username (str): Instagram username
        """
        data_path = Path("./data")
        data_path.mkdir(parents=True, exist_ok=True)
        end_date = datetime.today()
        formatted_end_date = end_date.strftime("%Y-%m-%-d")
        self.download_posts(
            data_path=data_path,
            start_date=conf["start_date"],
            end_date=formatted_end_date,
            username=username,
        )

    def update_downloaded_posts(self, username: str = credentials["USERNAME"]):
        """Update the downloaded posts by downloading the latest posts. First, check for the latest
        file in the data folder, and then download the latest posts continuing from there.

        Args:
            username (str): username of instagram profile
        """
        folder = Path(f"./data/{username}")
        if folder.exists():
            files = [f for f in folder.iterdir() if f.is_file()]
        else:
            logger.error("No data folder found. Please download the posts first.")
        file_datetime_list = []
        for file in files:
            datetime_str = file.name.split("_UTC")[0]
            file_datetime = datetime.strptime(datetime_str, "%Y-%m-%d_%H-%M-%S")
            file_datetime_list.append(file_datetime)
        file_datetime_list.sort(reverse=True)
        latest_file_datetime = file_datetime_list[0]
        start_date = latest_file_datetime + timedelta(minutes=1)
        # try rounding to nearest second to download posts (must be datetime object)
        end_date = datetime.today()
        self.download_posts(
            data_path=Path("./data"),
            start_date=start_date,
            end_date=end_date,
            username=username,
        )
        logger.info(f"updated {username} posts")

    def download_hastag_posts(self, hashtag):
        for post in instaloader.Hashtag.from_name(self.L.context, hashtag).get_posts():
            self.L.download_post(post, target="#" + hashtag)

    def get_users_followers(self, user_name):
        """Note: login required to get a profile's followers."""
        self.L.login(input("input your username: "), input("input your password: "))
        profile = instaloader.Profile.from_username(self.L.context, user_name)
        file = open("follower_names.txt", "a+")
        for followee in profile.get_followers():
            username = followee.username
            file.write(username + "\n")
            print(username)

    def get_users_followings(self, user_name):
        """Note: login required to get a profile's followings."""
        self.L.login(input("input your username: "), input("input your password: "))
        profile = instaloader.Profile.from_username(self.L.context, user_name)
        file = open("following_names.txt", "a+")
        for followee in profile.get_followees():
            username = followee.username
            file.write(username + "\n")
            print(username)


if __name__ == "__main__":
    cls = GetInstagramProfile()
    # cls.download_users_profile_picture("best_gadgets_2030")
    # cls.download_user_posts(credentials["USERNAME"])
    cls.update_downloaded_posts(credentials["USERNAME"])
    # cls.download_hastag_posts("gadgets")
    # cls.get_users_followers("best_gadgets_2030")
    # cls.get_users_followings("best_gadgets_2030")
