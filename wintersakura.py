#!/usr/bin/python3
import sys
from pprint import pprint
from urllib.parse import urljoin
import bs4
import requests
import os
import re

config_dict = {
    'site_name': 'wintersakura',
    'domain': 'https://wintersakura.net',
    'site_url': "https://wintersakura.net/torrents.php?sort=4&type=desc",
    # c_lang;
    'site_cookie': "c_lang; c_secure_uid=MTYzOTg%3D; c_secure_pass=e4e57957b26463802cdb5d4a5e949b1b; c_secure_ssl=eWVhaA%3D%3D; c_secure_tracker_ssl=eWVhaA%3D%3D; c_secure_login=bm9wZQ%3D%3D",
    'is_gazelle': False,
    'is_encrypted': False,
    'min_size': 5,
    'max_size': sys.maxsize,
    'torrents_amount': 5,
    'torrent_path': os.path.join(os.path.dirname(__file__), 'torrents'),
    'http_headers': {
        "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
        'Upgrade-Insecure-Requests': '1',
        'Dnt': '1',
        'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept_Language": 'en-AU,en;q=0.9',
        "Accept_Encoding": 'gzip, deflate, br',
        "Cache_Control": 'max-age=0',
        "Content_Length": '',
        "Content_Type": 'text/html; charset=utf-8; Cache-control:private',
        "Origin": '',
        "Referer": 'https://wintersakura.net/torrents.php',
    }
}


class HttpRequest:
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'

    def __init__(self, config):
        self.site_name = config["site_name"]
        self.domain = config["domain"]
        self.site_url = config["site_url"]
        self.site_cookie = config["site_cookie"]
        self.session = self.get_session()
        self.http_headers = self.get_headers(config['http_headers'])

    def request(self, url):
        if self.http_headers.get('User-Agent') or \
                self.http_headers.get('Referer') or \
                self.http_headers.get('Host'):
            res = self.session.get(url, headers=self.http_headers)
        else:
            res = self.session.get(url)
        return res

    def get_headers(self, config):
        '''
        Make a proper headers dictionary
        '''
        headers = {'User-Agent': self.user_agent}
        keys = ['Referer', 'Host', 'Accept', 'Accept-language', 'Accept-encoding', 'Origin', 'Dnt',
                'Upgrade-Insecure-Requests', 'Cache-control', 'Content-length', 'Content-type']

        for key in keys:
            if key in config:
                headers[key] = config.get(key, '')
        return headers

    def get_session(self):
        s = requests.Session()
        s.cookies.update({"cookie": self.site_cookie})
        return s


class NexusPage():
    '''
    Getting a torrent page with all torrents in it
    '''
    _torrents_class_name = '.torrentname'
    _HDC_torrents_class_name = '.t_name'
    is_encrypted = False
    free_tag = 'pro_free'
    free_tag2 = 'pro_free2up'
    pattern = r'id=(\d+)'
    colspan = '3'

    @property
    def torrents_class_name(self):
        if self.is_encrypted:
            return self._HDC_torrents_class_name
        else:
            return self._torrents_class_name

    def __init__(self, config):
        self.torrents_list = []
        self.torrents = []
        self.site_name = config['site_name']
        self.min_size = config['min_size']
        self.max_size = config['max_size']
        self.domain = config['domain']
        self.site_url = config['site_url']
        self.site_cookie = config['site_cookie']
        self.is_encrypted = config['is_encrypted']
        self.torrents_amount = config['torrents_amount']
        self.torrent_path = config['torrent_path']
        self.http_headers = config['http_headers']

        # Requesting page information of torrents by session
        self.http_client = HttpRequest(config)
        res = self.http_client.request(self.site_url)
        soup = bs4.BeautifulSoup(res.text, 'lxml')
        # print(res.text)
        self.get_all(res.text)

    def get_all(self, html):
        """get all torrents of the page"""
        soup = bs4.BeautifulSoup(html, 'lxml')
        self.torrents = soup.select('.torrents>tr')
        print(f'Found {len(self.torrents)} torrents')
        return self.torrents

    def get_free(self):
        """get all torrents of the page"""
        self.free_torrents = []

        for index, entry in enumerate(self.torrents):
            # if torrent is free:
            rate = 0
            if entry.find(class_=self.free_tag):
                rate = 1
            elif entry.find(class_=self.free_tag2):
                rate = 1
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
            size = self.get_size(str(entry))
            if size and download_url and detail_url:
                self.free_torrents.append((torrent_id, title, size, rate, detail_url, download_url))
            # print(entry)
            # print(torrent_id, title, size, detail_url)

        print(f'Found {len(self.free_torrents)}/{len(self.torrents)} free torrents')
        #pprint(self.free_torrents)
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
        log_path = os.path.join(self.torrent_path, "torrents.log")
        if not os.path.isfile(log_path):
            with open(log_path, 'w') as f:
                f.write("A list shows the torrents have been downloaded:\n")

        count = 0
        new = 0
        msg_body = ''
        for torrent_id, title, size, rate, detail_url, download_url in self.free_torrents:
            if count >= self.torrents_amount:
                break
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
                with open(log_path, 'a+') as f:
                    f.write(torrent_name + '\n')
            else:
                print(f'Skip {torrent_name}')

            count += 1

        with open(log_path, 'a+') as f:
            f.write("-------------------------------\n")
        if new > 0:
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


#####
class GazellePage():
    """Getting a torrent page with all torrents in it"""
    torrents_class_name = '.td_info'
    colspan = '3'

    def __init__(self):
        self.torrents_list = []
        self.processed_list = []

        # Requesting page information of torrents by session
        res = requests_check_headers(self.site_url)
        soup = bs4.BeautifulSoup(res.text, 'lxml')
        self.torrents_list = soup.select(self.torrents_class_name)

        # Choosing the first line or the last third line based on the site source code
        # self.processed_list = self.torrents_list
        for entry in self.torrents_list:
            if entry['colspan'] == self.colspan:
                self.processed_list.append(entry)


if __name__ == '__main__':

    if not config_dict['is_gazelle']:
        page = NexusPage(config_dict)
        # task_list = task.find_free()
        free_torrents = page.get_free()
        page.download_free()

    else:
        # The site would inform you that you have loged in this site when you run Page() at the very beginning.
        # task = GazellePage()
        # So just run this command again to make sure that you can get the informations of torrents page.
        page = GazellePage()
        # free_torrents = page.find_free(DIC_free_tag)
        # download_free(torrents_amount, free_torrents, torrent_path)
