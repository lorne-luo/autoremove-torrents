import sys
from datetime import datetime, timezone, timedelta
from pprint import pprint
from urllib.parse import urljoin
import bs4
import requests
import os
import re
import feedparser
from dateutil.parser import parse

from config import configs
from page import NexusPage, GazellePage

if __name__ == '__main__':

    for name, site_config in configs.items():
        print(f"Daily sign for {name}")

        if site_config.is_gazelle:
            page = GazellePage()
            # free_torrents = page.find_free(DIC_free_tag)
            # download_free( free_torrents, torrent_path)
        else:
            page = NexusPage(site_config)
            page.sign_daily()
