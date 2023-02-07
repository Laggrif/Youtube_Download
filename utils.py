import re


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
