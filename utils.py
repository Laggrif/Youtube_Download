import re

banned_urls = [
    '',
    'https://www.youtube.com/feed/subscriptions',
    'https://www.youtube.com/feed/library',
    'https://www.youtube.com/feed/history',
    'https://www.youtube.com/reporthistory',
    'https://www.youtube.com'
]
banned_url_content = [
    '/signin',
    'https://www.youtube.com/feed/',
    'https://www.youtube.com/account',
    'https://www.youtube.com/channel',
    'https://www.youtube.com/gaming',
    'https://www.youtube.com/premium'
]


def check_url(url: str):
    for i in banned_url_content:
        if url.__contains__(i):
            return False
    for i in banned_urls:
        if url == i or url == i + '/':
            return False
    if url.startswith('https://www.youtube.com'):
        return url.startswith('https://www.youtube.com/watch')
    return True


def time_to_int(time):
    if time == '∞':
        return float('inf')
    t = time.split(':')
    sec = 0
    for i in range(len(t)):
        sec += int(t[i]) * (60 ** (len(t) - 1 - i))
    return sec


def int_to_time(sec):
    h = int(sec / 3600)
    m = int(sec / 60 - h * 60)
    s = int(sec - m * 60 - h * 3600)
    if h == 0:
        time = f'{m:02}:{s:02}'
    else:
        time = f'{h:02}:{m:02}:{s:02}'
    return time


def str_to_int(string: str):
    return float(re.sub(r'[^0-9.]', "", string))


def str_minus_num(string: str):
    return re.sub(r'\d.', '', string)
