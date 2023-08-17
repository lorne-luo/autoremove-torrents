import os
import sys


class DefaultConfig:
    site_name = None
    domain = None
    site_url = None
    rss_url = None
    site_cookie = None
    is_gazelle = False
    is_encrypted = False

    min_size = 25  # torrent min GB size
    max_size = 140
    only_2x = False
    # torrent_path = os.path.join(os.path.dirname(__file__), 'torrents')
    torrent_path = '/data/pt/torrents'

    http_headers = {
        "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
    }


class HDArea(DefaultConfig):
    site_name = 'HDArea'
    domain = 'https://hdarea.club'
    site_url = "https://hdarea.club/torrents.php?sort=4&type=desc"
    daily_sign_url = "sign_in.php"
    rss_url = "https://hdarea.club/torrentrss.php?rows=10&isize=1&linktype=dl&passkey=70a7f5b7a2690e25ace71e4d14d46b0a"
    site_cookie = "c_lang; c_secure_uid=MTIzNDk0; c_secure_pass=7aa59fec74c5dfc1bd21e09f154269e2; c_secure_ssl=eWVhaA%3D%3D; c_secure_tracker_ssl=eWVhaA%3D%3D; c_secure_login=bm9wZQ%3D%3D"


class WinterSakura(DefaultConfig):
    site_name = 'WinterSakura'
    domain = 'https://wintersakura.net'
    site_url = "https://wintersakura.net/torrents.php?sort=4&type=desc"
    daily_sign_url = "attendance.php"
    rss_url = "https://wintersakura.net/torrentrss.php?passkey=693fcaab7778be73dbd0b593711fb191&rows=10&isize=1&linktype=dl"
    site_cookie = "c_lang; c_secure_uid=MTYzOTg%3D; c_secure_pass=e4e57957b26463802cdb5d4a5e949b1b; c_secure_ssl=eWVhaA%3D%3D; c_secure_tracker_ssl=eWVhaA%3D%3D; c_secure_login=bm9wZQ%3D%3D"


configs = {
    'hdarea': HDArea,
    'wintersakura': WinterSakura,
}
