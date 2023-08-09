#!/usr/bin/python3
import sys
from pprint import pprint
from urllib.parse import urljoin
from urllib.request import urlretrieve

import bs4
import requests
import os
import re

site_name = "cyanbug"
site_url = "https://cyanbug.net/torrents.php"
site_cookie = "c_lang; c_secure_uid=MTMxNjU%3D; c_secure_pass=ad6604e4c304946780791c0c56bee6d2; c_secure_ssl=eWVhaA%3D%3D; c_secure_tracker_ssl=eWVhaA%3D%3D; c_secure_login=bm9wZQ%3D%3D"

# It always would be the first part of your site, like: url_half = "https://tp.m-team.cc/"
domain = "https://cyanbug.net/"

# If your site is a Gazelle Site, please change this varible to True, like: is_gazelle = True
is_gazelle = False

# If the torrents' download url in your site were encrypted like HDC, please change this varible to True, like: is_encrypted = True
is_encrypted = False

# Check the download url, especially when you are using a https(SSL) url.
# Some torrents' download pages url could be "https://tp.m-team.cc/download.php?id=xxxxx&https=1", in this case, you need to assign the variable of "url_last". Examples:
# url_last = "&https=1"
# url_last = ""


# If you couldn't downlaod the torrents to your directory where the *.py script is, you could just define the variables below. Make sure the format of your path because of the difference between Windows and Linux.
# Example of windows:              monitor_path = r'C:\\Users\\DELL-01\\Desktop\\'       Don't forget the last '\\'
# Example of Linux and MacOS:      monitor_path = r'/home/user/Downloads/'               Don't forget the last '/'
torrent_path = r'/Users/lorneluo/Downloads/'

# Other informations for safer sites. Complete it if you cannot download torrents.
# Some examples: 
# user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'
# referer = 'https://tp.m-team.cc/login.php'
# host = 'tp.m-team.cc'

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'

# You don't need to define the variables shows below unless you couldn't download the torrents after defined the above one
referer = ''
host = ''

# You don't need to define the variables shows below unless you couldn't download the torrents after defined the above two
upgrade_insecure_requests = ''
dnt = ''
accept_language = ''
accept_encoding = ''
accept = ''
cache_control = ''
content_length = ''
content_type = ''
origin = ''

# Only if you just want to check the first 10 torrents is free in the page and download the free torrents in this small amount, please change it to 10
# like: torrents_amount = 10
# We always grab all the torrents in the whole page, but you can define the amount of grabing torrents by defining the variable below 
torrents_amount = 2

# You don't need to change this variables unless you cannot download from your GAZELLE site
# check this value from the page source code
colspan = '3'

# You don't need to change this variables unless you cannot find free torrents correctly
free_tag = 'pro_free'
free_tag2 = 'pro_free2up'
DIC_free_tag = 'torrent_label tooltip tl_free'
# PTP_free_tag = 'torrent-info__download-modifier--free'


# PTP_torrents_class_name = '.basic-movie-list__torrent-row--user-seeding'

download_class_name = '.rowfollow'
HDC_download_class_name = '.torrentdown_button'

##^^^^^^^^^^^^^^^^^^^^^^^ YOU ONLY NEED TO ASSIGN VARIABLES SHOWS BEFORE ^^^^^^^^^^^^^^^^^^^^^^^^^^^##


# Using Session to keep cookie
cookie_dict = {"cookie": site_cookie}
s = requests.Session()
s.cookies.update(cookie_dict)
pattern = r'id=(\d+)'

config_dict = {
    'site_name': 'cyanbug',
    'domain': 'cyanbug',
    'site_url': "https://cyanbug.net/torrents.php",
    'is_gazelle': False,
    'is_encrypted': False,
    'torrents_amount': 10,
    'torrent_path': r'/Users/lorneluo/Downloads/',
    'headers': {

    }
}


class HttpRequest:
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'

    def __init__(self, config):
        self.headers = self.get_headers(config['headers'])
        self.site_name = config["site_name"]
        self.domain = config["domain"]
        self.site_url = config["site_url"]
        self.session = self.get_session()

    def request(self, url):
        if self.headers.get('User-Agent') or \
                self.headers.get('Referer') or \
                self.headers.get('Host'):
            res = s.get(url, headers=self.headers)
        else:
            res = s.get(url)
        return res

    def get_headers(self, config):
        '''
        Make a proper headers dictionary
        '''
        headers = {'User-Agent': self.user_agent}
        keys = ['Referer', 'Host', 'Accept', 'Accept-language', 'Accept-encoding', 'Origin', 'dnt',
                'Upgrade-insecure-requests', 'Cache-control', 'Content-length', 'Content-type']

        for key in keys:
            if key in config:
                headers[key] = config.get(key, '')
        return headers

    def get_session(self):
        s = requests.Session()
        s.cookies.update({"cookie": site_cookie})
        return s


def get_headers(config):
    '''
    Make a proper headers dictionary
    '''
    headers = {}
    keys = ['User-Agent', 'Referer', 'Host', 'accept', 'accept-language', 'accept-encoding', 'origin', 'dnt',
            'upgrade-insecure-requests', 'cache-control', 'content-length', 'content-type']

    for key in keys:
        if key in config:
            headers[key] = config.get(key, '')
    return headers


my_headers = get_headers(config_dict)


#####
def requests_check_headers(url):
    if user_agent or referer or host:
        res = s.get(url, headers=my_headers)
    else:
        res = s.get(url)
    return res


#####
class Torrents():
    '''
    Define a torrent
    '''

    def __init__(self, *args):
        self.torrent = args
        self.is_free = args[0]
        self.torrent_id = args[1]
        self.detail_url = args[2]
        self.download_url = args[3]

    def __str__(self):
        return '{}_{}.torrent'.format(site_name, self.torrent_id)

    def download(self):
        '''
        A function to download a free torrent.
        '''
        down_url = urljoin(domain, self.download_url)  # + url_last
        if self.is_free:
            res = requests_check_headers(down_url)
            # vvvvvvvvvvvvvvvvvvvvv# Command for debug #vvvvvvvvvvvvvvvvv# Command for debug #vvvvvvvvvvvvvvvvvvvvvv#
            print('\n\nPrinting the download statements: ')
            try:
                print('Downloading' + self.__str__())
            except:
                print('Cannot print the torrent name.')
            try:
                print('Writing torrent to your path ...')
                # ^^^^^^^^^^^^^^^^^^^^^# Command for debug #^^^^^^^^^^^^^^^^^# Command for debug #^^^^^^^^^^^^^^^^^^^^^^#
                with open(torrent_path + self.__str__(), 'wb') as f:
                    f.write(res.content)
            # vvvvvvvvvvvvvvvvvvvvv# Command for debug #vvvvvvvvvvvvvvvvv# Command for debug #vvvvvvvvvvvvvvvvvvvvvv#
            except:
                print('Cannot write torrent file in your path!!')
        # ^^^^^^^^^^^^^^^^^^^^^# Command for debug #^^^^^^^^^^^^^^^^^# Command for debug #^^^^^^^^^^^^^^^^^^^^^^#
        else:
            pass

    def encrypted_download(self, download_class_name):
        '''
        A function to download a free torrent.
        '''
        download_page = domain + self.torrent[2]
        if self.torrent[0]:
            response = requests_check_headers(download_page)
            soup = bs4.BeautifulSoup(response.text, 'lxml')
            # down_url_last = soup.select_one(download_class_name).a['href']   # For other sites
            down_url_last = soup.select_one(download_class_name)[
                'href']  # Just for HDC, common way, but different from other sites either
            down_url = domain + down_url_last
            # down_url = soup.select_one('#clip_target')['href']    # a faster way For HDC only
            res = requests_check_headers(down_url)
            # vvvvvvvvvvvvvvvvvvvvv# Command for debug #vvvvvvvvvvvvvvvvv# Command for debug #vvvvvvvvvvvvvvvvvvvvvv#
            print('\n\nPrinting the download statements: ')
            try:
                print('Downloading' + self.__str__())
            except:
                print('Cannot print the torrent name.')
            try:
                print('Writing torrent to your path ...')
                # ^^^^^^^^^^^^^^^^^^^^^# Command for debug #^^^^^^^^^^^^^^^^^# Command for debug #^^^^^^^^^^^^^^^^^^^^^^#
                with open(torrent_path + self.__str__(), 'wb') as f:
                    f.write(res.content)
            # vvvvvvvvvvvvvvvvvvvvv# Command for debug #vvvvvvvvvvvvvvvvv# Command for debug #vvvvvvvvvvvvvvvvvvvvvv#
            except:
                print('Cannot write torrent file in your path!!')
        # ^^^^^^^^^^^^^^^^^^^^^# Command for debug #^^^^^^^^^^^^^^^^^# Command for debug #^^^^^^^^^^^^^^^^^^^^^^#
        else:
            pass


#####
class NexusPage():
    '''
    Getting a torrent page with all torrents in it
    '''
    _torrents_class_name = '.torrentname'
    _HDC_torrents_class_name = '.t_name'
    is_encrypted = False
    free_tag = 'pro_free'
    free_tag2 = 'pro_free2up'

    @property
    def torrents_class_name(self):
        if self.is_encrypted:
            return self._HDC_torrents_class_name
        else:
            return self._torrents_class_name

    def __init__(self, site_name, domian, site_url, is_encrypted, torrents_amount, torrent_path):
        self.torrents_list = []
        self.processed_list = []
        self.site_name = site_name
        self.domian = domian
        self.site_url = site_url
        self.is_encrypted = is_encrypted
        self.torrents_amount = torrents_amount
        self.torrent_path = torrent_path

        # Requesting page information of torrents by session

        res = requests_check_headers(site_url)
        soup = bs4.BeautifulSoup(res.text, 'lxml')
        self.processed_list = soup.select(self.torrents_class_name)
        self.get_all(res.text)

        # vvvvvvvvvvvvvvvvvvvvv# Command for debug #vvvvvvvvvvvvvvvvv# Command for debug #vvvvvvvvvvvvvvvvvvvvvv#
        # print('\n\nThe website shows: ')
        # try:
        #     print(str(soup))
        # except:
        #     print('Cannot print soup')
        # print('\n\nThe torrents informations(processed_list) shows below: ')
        # try:
        #     print(self.processed_list)
        # except:
        #     print('Cannot print processed_list')

    def get_all(self, html):
        """get all torrents of the page"""
        soup = bs4.BeautifulSoup(html, 'lxml')
        self.torrents = soup.select('.torrents>tr')
        return self.torrents

    def get_free(self):
        """get all torrents of the page"""
        self.free_torrents = {}

        for index, entry in enumerate(self.torrents):
            # if torrent is free:
            if not entry.find(class_=self.free_tag) and not entry.find(class_=self.free_tag2):
                continue

            detail_url = None
            download_url = None
            for a in entry.find_all('a', href=True):
                if a['href'].startswith('details.php'):
                    detail_url = a['href']
                if a['href'].startswith('download.php'):
                    download_url = a['href']

            if not detail_url:
                continue

            torrent_id = re.search(pattern, detail_url).group(1)
            size = self.get_size(str(entry))
            if size:
                self.free_torrents[torrent_id] = (torrent_id, size, download_url)

        # pprint(len(self.torrents))
        pprint(self.free_torrents)
        return self.free_torrents

    def __str__(self):
        return self.processed_list

    def get_size(self, text):
        pattern = '>(\d+\.\d+).*GB<'
        match = re.search(pattern, text)
        if match:
            size = match.group(1)
            return size
        else:
            return None

    def get_download_url(self, torrent_id):
        return f'{self.domian}/download.php?id={torrent_id}'

    def download(self, url, path):
        res = requests_check_headers(url)
        with open(path, 'wb') as f:
            f.write(res.content)
        print(f'download {url} to {path}')

    def download_free(self):
        if os.path.isfile(self.torrent_path + "downloaded_list.log") == False:
            with open(self.torrent_path + "downloaded_list.log", 'w') as f:
                f.write("A list shows the torrents have been downloaded:\n")

        count = 0
        for torrent_id, (_id, size, download_url) in self.free_torrents.items():
            if count >= self.torrents_amount:
                break

            full_download_url = urljoin(self.domian, download_url)
            torrent_name = f'{self.site_name}_{torrent_id}_{size}GB.torrent'

            log_path = os.path.join(self.torrent_path, "torrents.log")
            try:
                with open(log_path, 'r+') as f:
                    downloaded = f.read()
                    if torrent_name in downloaded:
                        continue
            except Exception as ex:
                pass
            with open(log_path, 'a+') as f:
                f.write(torrent_name + '\n')

            torrent_path = os.path.join(self.torrent_path, torrent_name)
            if not os.path.isfile(torrent_path):
                self.download(full_download_url, torrent_path)
                print(f'Save {torrent_path}')
            else:
                print(f'Skip {torrent_path}')

            count += 1

    def find_free(self):
        free_list = []
        # Check free and add states
        for index, entry in enumerate(self.processed_list):

            details = entry.a['href']

            links = entry.find_all('a', href=True)
            detail_url = None
            download_url = None
            if index == 0:
                print('entry')
                print(entry)
                for a in entry.find_all('a', href=True):
                    if a['href'].startswith('details.php'):
                        detail_url = a['href']
                    if a['href'].startswith('download.php'):
                        download_url = a['href']
                print(detail_url)
                print(download_url)

            torrent_id = re.search(pattern, details).group(1)

            # if torrent is free:
            if entry.find(class_=self.free_tag) or entry.find(class_=self.free_tag2):
                last_download_url = 'NULL'
                # Find the tag that download url in
                for subentry in entry.select('.embedded'):
                    if 'href="download.php?' in str(subentry):
                        last_download_url = subentry.a['href']
                free_list.append((True, torrent_id, details, last_download_url))
            else:
                free_list.append((False, torrent_id, details, "NULL"))
        # vvvvvvvvvvvvvvvvvvvvv# Command for debug #vvvvvvvvvvvvvvvvv# Command for debug #vvvvvvvvvvvvvvvvvvvvvv#
        print("\n\nThe torrents' free state tuples list shows below2: ")
        try:
            print(free_list)
        except:
            print('Cannot print the free_tuple_list')
        # ^^^^^^^^^^^^^^^^^^^^^# Command for debug #^^^^^^^^^^^^^^^^^# Command for debug #^^^^^^^^^^^^^^^^^^^^^^#
        self.free_list = free_list
        return free_list


#####
class GazellePage():
    """Getting a torrent page with all torrents in it"""
    torrents_class_name = '.td_info'

    def __init__(self):
        self.torrents_list = []
        self.processed_list = []

        # Requesting page information of torrents by session
        res = requests_check_headers(site_url)
        soup = bs4.BeautifulSoup(res.text, 'lxml')
        self.torrents_list = soup.select(self.torrents_class_name)

        # Choosing the first line or the last third line based on the site source code
        # self.processed_list = self.torrents_list
        for entry in self.torrents_list:
            if entry['colspan'] == colspan:
                self.processed_list.append(entry)
        # vvvvvvvvvvvvvvvvvvvvv# Command for debug #vvvvvvvvvvvvvvvvv# Command for debug #vvvvvvvvvvvvvvvvvvvvvv#
        # print('\n\nThe website shows: ')
        # try:
        #     print(str(soup))
        # except:
        #     print('Cannot print soup')
        # print('\n\nThe torrents informations(processed_list) shows below: ')
        # try:
        #     print(self.processed_list)
        # except:
        #     print('Cannot print processed_list')

    def __str__(self):
        return self.processed_list

    def find_free(self, free_tag, free_tag2=''):
        free_list = []
        # Check free and add states
        for entry in self.processed_list:
            last_download_url = entry.a['href']
            torrent_id = re.search(pattern, last_download_url).group(1)
            details = 'torrents.php?id=' + torrent_id

            # if torrent is free:
            if entry.find(class_=free_tag) or entry.find(class_=free_tag2):
                free_list.append((True, torrent_id, details, last_download_url))
            else:
                free_list.append((False, torrent_id, details, last_download_url))
        # vvvvvvvvvvvvvvvvvvvvv# Command for debug #vvvvvvvvvvvvvvvvv# Command for debug #vvvvvvvvvvvvvvvvvvvvvv#
        print("\n\nThe torrents' free state tuples list shows below1: ")
        try:
            print(free_list)
        except:
            print('Cannot print the free_tuple_list')
        # ^^^^^^^^^^^^^^^^^^^^^# Command for debug #^^^^^^^^^^^^^^^^^# Command for debug #^^^^^^^^^^^^^^^^^^^^^^#
        self.free_list = free_list
        return free_list


#####
def download_free(torrents_amount, task_list, monitor_path):
    if os.path.isfile(monitor_path + "downloaded_list.log") == False:
        with open(monitor_path + "downloaded_list.log", 'w') as f:
            f.write("A list shows the torrents have been downloaded:\n")

    if not torrents_amount:
        for torrent in task_list:
            torrent_name = str(Torrents(torrent))
            with open(monitor_path + "downloaded_list.log", 'r') as f:
                downloaded = f.read()
                if torrent_name in downloaded:
                    continue
            with open(monitor_path + "downloaded_list.log", 'a') as f:
                f.write(torrent_name + '\n')

            if os.path.isfile(monitor_path + torrent_name) == False:
                Torrents(torrent).download()
            else:
                continue
    else:
        for torrent in task_list[0:torrents_amount:1]:
            torrent_name = str(Torrents(torrent))

            with open(monitor_path + "downloaded_list.log", 'r') as f:
                downloaded = f.read()
                if torrent_name in downloaded:
                    continue
            with open(monitor_path + "downloaded_list.log", 'a') as f:
                f.write(torrent_name + '\n')

            if os.path.isfile(monitor_path + torrent_name) == False:
                Torrents(torrent).download()
            else:
                continue


#####
def download_encrypted_free(torrents_amount, task_list, monitor_path, download_class_name):
    if os.path.isfile(monitor_path + "downloaded_list.log") == False:
        with open(monitor_path + "downloaded_list.log", 'w') as f:
            f.write("A list shows the torrents have been downloaded:\n")

    if not torrents_amount:
        for torrent in task_list:
            torrent_name = str(Torrents(torrent))

            with open(monitor_path + "downloaded_list.log", 'r') as f:
                downloaded = f.read()
                if torrent_name in downloaded:
                    continue
            with open(monitor_path + "downloaded_list.log", 'a') as f:
                f.write(torrent_name)

            if os.path.isfile(monitor_path + torrent_name) == False:
                Torrents(torrent).encrypted_download(download_class_name)
            else:
                continue
    else:
        for torrent in task_list[0:torrents_amount:1]:
            torrent_name = str(Torrents(torrent))

            with open(monitor_path + "downloaded_list.log", 'r') as f:
                downloaded = f.read()
                if torrent_name in downloaded:
                    continue
            with open(monitor_path + "downloaded_list.log", 'a') as f:
                f.write(torrent_name)

            if os.path.isfile(monitor_path + torrent_name) == False:
                Torrents(torrent).encrypted_download(download_class_name)
            else:
                continue


def download_test(torrents_amount, task_list, monitor_path):
    if os.path.isfile(monitor_path + "downloaded_list.log") == False:
        with open(monitor_path + "downloaded_list.log", 'w') as f:
            f.write("A list shows the torrents have been downloaded:\n")

    for torrent in task_list[:torrents_amount] if torrents_amount else task_list:
        torrent_name = str(Torrents(torrent))

        with open(monitor_path + "downloaded_list.log", 'r') as f:
            downloaded = f.read()
            if torrent_name in downloaded:
                continue
        with open(monitor_path + "downloaded_list.log", 'a') as f:
            f.write(torrent_name + '\n')

        if not os.path.isfile(monitor_path + torrent_name):
            Torrents(torrent).download()


if __name__ == '__main__':
    if not is_gazelle:
        page = NexusPage(site_name, domain, site_url, is_encrypted, torrents_amount, torrent_path)
        # task_list = task.find_free()
        free_torrents = page.get_free()
        page.download_free()

        sys.exit()
        if not is_encrypted:
            download_free(torrents_amount, free_torrents, torrent_path)
        else:
            download_encrypted_free(torrents_amount, free_torrents, torrent_path, HDC_download_class_name)
    else:
        # The site would inform you that you have loged in this site when you run Page() at the very beginning.
        # task = GazellePage()
        # So just run this command again to make sure that you can get the informations of torrents page.
        page = GazellePage()
        free_torrents = page.find_free(DIC_free_tag)
        download_free(torrents_amount, free_torrents, torrent_path)
