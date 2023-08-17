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
    config_name = sys.argv[1]
    config = configs[config_name]

    print(f'Run for {config_name}')

    if config.is_gazelle:
        page = GazellePage()
        # free_torrents = page.find_free(DIC_free_tag)
        # download_free( free_torrents, torrent_path)
    else:
        page = NexusPage(config)
        page.run()
