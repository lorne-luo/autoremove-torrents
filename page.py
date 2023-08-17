import pickle
import shutil
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


class HttpRequest:
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'

    def __init__(self, config):
        self.site_name = config.site_name
        self.domain = config.domain
        self.site_url = config.site_url
        self.site_cookie = config.site_cookie
        self.session = self.get_session()
        self.http_headers = self.get_headers(config.http_headers)

    def request(self, url):
        if self.http_headers.get('User-Agent') or \
                self.http_headers.get('Referer') or \
                self.http_headers.get('Host'):
            res = self.session.get(url, headers=self.http_headers)
        else:
            res = self.session.get(url)
        return res

    def get_headers(self, config_headers):
        """Make a proper headers dictionary"""
        headers = {'User-Agent': self.user_agent}
        keys = ['User-Agent', 'Referer', 'Host', 'Accept', 'Accept-language', 'Accept-encoding', 'Origin', 'Dnt',
                'Upgrade-Insecure-Requests', 'Cache-control', 'Content-length', 'Content-type']

        for key in keys:
            if key in config_headers:
                headers[key] = config_headers.get(key, '')
        return headers

    def get_session(self):
        s = requests.Session()
        s.cookies.update({"cookie": self.site_cookie})
        return s


class NexusPage:
    """Getting a torrent page with all torrents in it"""
    _torrents_class_name = '.torrentname'
    _HDC_torrents_class_name = '.t_name'
    free_tag = 'pro_free'
    free_tag2 = 'pro_free2up'
    pattern = r'id=(\d+)'
    colspan = '3'
    interval = 120  # second
    only_2x = True
    rss_ids = []
    clean_old_minutes = 120

    @property
    def torrents_class_name(self):
        if self.is_encrypted:
            return self._HDC_torrents_class_name
        else:
            return self._torrents_class_name

    def __init__(self, config):
        self.torrents_list = []
        self.torrents = []
        self.rss_url = config.rss_url
        self.site_name = config.site_name
        self.min_size = config.min_size
        self.max_size = config.max_size
        self.domain = config.domain
        self.daily_sign_url = config.daily_sign_url
        self.site_url = config.site_url
        self.site_cookie = config.site_cookie
        self.is_encrypted = config.is_encrypted
        self.torrent_path = os.path.join(config.torrent_path, self.site_name)

        if not os.path.isdir(self.torrent_path):
            os.makedirs(self.torrent_path, exist_ok=True)

        # Requesting page information of torrents by session
        self.http_client = HttpRequest(config)
        self.log_path = os.path.join(self.torrent_path, "torrents.log")

    def run(self):
        self.rss_ids = self.get_rss()
        print(f'Filter {len(self.rss_ids)} rss')

        self.get_all()
        self.get_free()
        self.download_free()
        self.delete_old_torrents()

    def get_rss(self):
        self.rss_ids = {}
        res = self.http_client.request(self.rss_url)
        feeds = feedparser.parse(res.text)
        entries = feeds.entries

        print(f'Get {len(entries)} rss')

        entries = feeds.entries
        for entry in entries:
            match = re.search(self.pattern, entry.link)
            if match:
                torrent_id = match.group(1)
            else:
                continue

            dt = parse(entry.published)
            utcnow = datetime.now(timezone.utc)
            delta = utcnow - dt
            if delta.seconds < self.interval * 2:
                self.rss_ids[torrent_id] = dt
            # else:
            #     print(f'Skip [{torrent_id}]{entry.title}')

        # pprint(self.rss_ids)
        return self.rss_ids

    def delete_old_torrents(self):
        # Calculate the time 1 day ago
        current_time = datetime.now()
        threshold = current_time - timedelta(hours=self.clean_old_minutes)

        # Walk through the folder
        for root, dirs, files in os.walk(self.torrent_path):
            for file_name in files:
                if not file_name.endswith('.torrent'):
                    continue
                file_path = os.path.join(root, file_name)
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                # Compare the file's modification time with one day ago
                if file_time < threshold:
                    os.remove(file_path)
                    with open(self.log_path, 'a+') as f:
                        f.write(f"Deleted {os.path.basename(file_path)}." + '\n')

    def get_all(self):
        """get all torrents of the page"""
        res = self.http_client.request(self.site_url)
        # print(res.text)
        soup = bs4.BeautifulSoup(res.text, 'lxml')
        self.torrents = soup.select('.torrents>tr')
        # print(f'Found {len(self.torrents)} torrents')
        return self.torrents

    def get_free(self):
        """get all torrents of the page"""
        self.free_torrents = []

        for index, entry in enumerate(self.torrents):
            # if torrent is free:
            rate = 0
            if entry.find(class_=self.free_tag):
                if self.only_2x:
                    continue
                rate = 1
            elif entry.find(class_=self.free_tag2):
                rate = 2
            else:
                continue

            detail_url = None
            download_url = None
            title = None

            for a in entry.find_all('a', href=True):
                if a['href'].startswith('details.php'):
                    detail_url = a['href']
                if a['href'].startswith('download.php'):
                    download_url = a['href'] + '&letdown=1'

            for b in entry.find('b'):
                title = b.text.replace(' ', '.')
            if not detail_url:
                continue

            torrent_id = re.search(self.pattern, detail_url).group(1)
            if torrent_id not in self.rss_ids:
                continue

            size = self.get_size(str(entry))
            if size and download_url and detail_url:
                self.free_torrents.append((torrent_id, title, size, rate, detail_url, download_url))
            # print(entry)
            # print(torrent_id, title, size, detail_url)

        print(f'Found {len(self.free_torrents)}/{len(self.torrents)} free torrents')
        # pprint(self.free_torrents)
        return self.free_torrents

    def get_size(self, text):
        pattern = '>(\d+\.\d+).*GB<'
        match = re.search(pattern, text)
        if match:
            size = match.group(1)
            return float(size)
        else:
            return None

    def get_download_url(self, torrent_id):
        return f'{self.domain}/download.php?id={torrent_id}&letdown=1'

    def download_free(self):
        if not os.path.isfile(self.log_path):
            with open(self.log_path, 'w') as f:
                f.write("A list shows the torrents have been downloaded:\n")

        count = 0
        new = 0
        msg_body = ''
        for torrent_id, title, size, rate, detail_url, download_url in self.free_torrents:
            if not self.min_size < size < self.max_size:
                continue

            full_download_url = urljoin(self.domain, download_url)
            full_detail_url = urljoin(self.domain, detail_url)
            torrent_name = f'{torrent_id}_{title}_{self.site_name}_{size}GB_{rate}X.torrent'

            torrent_path = os.path.join(self.torrent_path, torrent_name)
            if not os.path.isfile(torrent_path):
                if self.is_encrypted:
                    self.encrypted_download(full_detail_url, torrent_path)
                else:
                    self.download(full_download_url, torrent_path)
                # print(f'Save {torrent_path}')
                new += 1
                msg_body += f'[{torrent_id}]{title} {size}GB {rate}X\n'
                with open(self.log_path, 'a+') as f:
                    f.write(f"{datetime.now().strftime('%m-%d %H:%M')}: {torrent_name}\n")
            else:
                print(f'Skip {torrent_name}')

            count += 1

        if new > 0:
            with open(self.log_path, 'a+') as f:
                f.write("-------------------------------\n")
            msg_title = f'{new} new torrent for {self.site_name}'
            notify_url = f'https://iyuu.cn/IYUU27977T0794db8e218f9becae662453091e9c90fc6edb78.send?text={msg_title}&desp={msg_body}'
            requests.get(notify_url)

    def download(self, url, path):
        res = self.http_client.request(url)
        with open(path, 'wb') as f:
            f.write(res.content)
        print(f'download {url} to {os.path.basename(path)}')

    def encrypted_download(self, full_detail_url, path):
        '''
        A function to download a free torrent.
        '''
        response = self.http_client.request(full_detail_url)
        soup = bs4.BeautifulSoup(response.text, 'lxml')
        down_url_last = soup.select_one(self._HDC_torrents_class_name)[
            'href']  # Just for HDC, common way, but different from other sites either
        down_url = urljoin(self.domain, down_url_last)
        # down_url = soup.select_one('#clip_target')['href']    # a faster way For HDC only
        res = self.http_client.request(down_url)
        with open(path, 'wb') as f:
            f.write(res.content)
        print(f'download {down_url} to {path}')

    def get_torrents_info(self):
        """
        {'average_download_speed': 4043771,
         'average_upload_speed': 398547,
         'category': [],
         'connected_seeder': 1,
         'connected_leecher': 38,
         'leecher': 77,
         'create_time': 1691847202,
         'download_speed': 1168245,
         'downloaded': 10542112361,
         'last_activity': 1.792027235031128,
         'name': 'mingchao',
         'progress': 0.0710105176079218,
         'ratio': 0.0985584192636552,
         'seeder': 4,
         'seeding_time': 0,
         'size': 148461584384,
         'stalled': False,
         'status': 'Downloading',
         'upload_speed': 1377327,
         'uploaded': 1039013930}
        """
        try:
            with open('torrent.pickle', 'rb') as handle:
                data = pickle.load(handle)
                return data
        except:
            return None

    def sign_daily(self):
        sign_url = urljoin(self.domain, self.daily_sign_url)
        res = self.http_client.request(sign_url)
        print(res.text)


class GazellePage():
    """Getting a torrent page with all torrents in it"""
    torrents_class_name = '.td_info'
    colspan = '3'

    def __init__(self):
        self.torrents_list = []
        self.processed_list = []

        # # Requesting page information of torrents by session
        # res = requests_check_headers(self.site_url)
        # soup = bs4.BeautifulSoup(res.text, 'lxml')
        # self.torrents_list = soup.select(self.torrents_class_name)
        #
        # # Choosing the first line or the last third line based on the site source code
        # # self.processed_list = self.torrents_list
        # for entry in self.torrents_list:
        #     if entry['colspan'] == self.colspan:
        #         self.processed_list.append(entry)
