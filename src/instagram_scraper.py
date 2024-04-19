import csv
from datetime import datetime
from itertools import dropwhile, takewhile

import instaloader
import yaml

from logs.logging import logger

with open("credentials.yml", "r") as file:
    credentials = yaml.safe_load(file)


class GetInstagramProfile:
    def __init__(self) -> None:
        self.L = instaloader.Instaloader()
        self.L.login(credentials["USERNAME"], credentials["PASSWORD"])

    def download_users_profile_picture(self, username):
        self.L.download_profile(username, profile_pic_only=True)

    def download_users_posts_with_periods(self, username: str):
        """Creates a new folder that is named as the Instagram Username, and downloads all the posts - text file, pictures in jpg, video in mp4.
        These files are named by the date posted.

        Args:
            username (str): Instagram username
        """
        posts = instaloader.Profile.from_username(self.L.context, username).get_posts()
        SINCE = datetime(2019, 8, 28)
        UNTIL = datetime(2024, 9, 30)

        for post in takewhile(
            lambda p: p.date > SINCE, dropwhile(lambda p: p.date > UNTIL, posts)
        ):
            self.L.download_post(post, username)

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
    cls.download_users_posts_with_periods(credentials["USERNAME"])
    # cls.download_hastag_posts("gadgets")
    # cls.get_users_followers("best_gadgets_2030")
    # cls.get_users_followings("best_gadgets_2030")
