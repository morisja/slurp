#!/usr/bin/env python3

from typing import NamedTuple
from google.cloud import storage
import click
import json
import os
import eyed3
from collections import namedtuple

from pathlib import Path
from feedgen.feed import FeedGenerator
from google.cloud.storage import bucket

SourceDest = namedtuple("SourceDest", "source_file_name destination_blob_name")

BUCKET_NAME = os.getenv("BUCKET_NAME")
FEED_NAME = os.getenv("FEED_NAME")
TITLE = os.getenv("TITLE")


class StorageManager:

    def __init__(self, bucket_name=BUCKET_NAME):
        self.bucket_name = bucket_name

    def upload_blobs(self, source_dests):
        for sd in source_dests:
            self.upload_blob(sd.source_file_name, sd.destination_blob_name)

    def upload_blob(self, source_file_name, destination_blob_name):
        """Uploads a file to the bucket."""
        storage_client = storage.Client()
        bucket = storage_client.bucket(self.bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_name)

    def upload_string(self, string, destination_blob_name):
        storage_client = storage.Client()
        bucket = storage_client.bucket(self.bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_string(string)

    def list_pods(self, prefix="pods/"):
        return storage.Client().list_blobs(self.bucket_name, prefix=prefix)        

    def list_blobs(self, prefix=None):
        """Lists all the blobs in the bucket."""
        storage_client = storage.Client()
        # Note: Client.list_blobs requires at least package version 1.17.0.
        blobs = storage_client.list_blobs(self.bucket_name)
        for blob in blobs:
            print(blob.name)


class FeedManager:
    def __init__(self, feed_name, title, bucket_name=BUCKET_NAME, storage_manager=StorageManager()):
        self.storage_manager = storage_manager
        self.feed_name = feed_name
        self.title = title
        self.bucket_name=bucket_name

    def get_feed(self):
        fg = FeedGenerator()
        fg.load_extension("podcast")
        fg.podcast.itunes_category("Technology", "Podcasting")
        fg.id("http://www.null.com")
        fg.title(self.feed_name)
        fg.description(self.feed_name)
        fg.link(href="http://www.null.com/test.atom", rel="self")
        return fg

    def add_entry(self, fg, fname, hash):
        fe = fg.add_entry()
        fe.title(self.title)
        fe.id(f"http:///www.null.com/{hash}")
        fe.description(self.title)
        fe.link(href="http://www.null.com", rel="alternate")
        fe.enclosure(fname, 0, "audio/mpeg")

    def gen_podcast_feed(self):
        blobs = sorted(self.storage_manager.list_pods(), key=lambda k: k.time_created)
        pods = []
        for blob in blobs:
            if "json" in blob.name:
                detail = json.loads(blob.download_as_string().decode())
                detail["fname"] = blob.name
                detail["hash"] = blob.crc32c
                pods.append(detail)

        fg = self.get_feed()
        for pod in pods:
            self.add_entry(
                fg,
                f"http://{self.bucket_name}/" + pod["fname"].replace(".json", ".mp3"),
                pod["hash"],
            )
        self.storage_manager.upload_string(fg.rss_str(pretty=True), "today.xml")


@click.group()
@click.pass_context
def main(ctx):
    pass


@main.command()
@click.pass_context
@click.option("--file", required=True)
def upload_pod(ctx, file):
    fname_mp3 = Path(file)
    fname_json = fname_mp3.with_suffix(".json")

    s = StorageManager()
        
    s.upload_blobs(
        [
            SourceDest(fname_mp3, "pods/" + fname_mp3.name),
            SourceDest(fname_json, "pods/" + fname_json.name),
        ]
    )


@main.command()
@click.pass_context
@click.option("--file", required=True)
def write_tag_cache(ctx, file):
    p = Path(file)
    f = eyed3.load(p)
    tags = {"title": f.tag.title}
    with open(p.with_suffix(".json"), "w") as f:
        print(json.dumps(tags, indent=4), file=f)


@main.command()
@click.pass_context
def list_all(ctx):
    StorageManager().list_blobs()


@main.command()
@click.pass_context
def gen_feed(ctx):
    FeedManager(feed_name=FEED_NAME, title=TITLE).gen_podcast_feed()


def start():
    main(obj={})


if __name__ == "__main__":
    start()
