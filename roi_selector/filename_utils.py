import os
import re
from datetime import datetime


def rmprefix(prefix, text):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text

def rmsuffix(suffix, text):
    if text.endswith(suffix):
        return text[:-len(suffix)]
    return text

def clean_filename(filename):
    return re.sub('[~]', '', filename)

def get_camera_name(filename):
    return os.path.basename(filename)[:12]

def date_from_filename(prefix, suffix, filename):
    filename = clean_filename(filename)
    filename = rmprefix(prefix, filename)
    ts_str = rmsuffix(suffix, filename)
    try:
        ts = datetime.strptime(ts_str, '%Y%m%d-%H%M%S%f')
        return ts
    except ValueError:
        print('Not a valid date: ', ts_str)
        pass

def gather_files(directory, suffix):
    files = []
    for fn in os.listdir(directory):
        if fn.endswith(suffix):
            files.append(fn)

    return files

if __name__ == '__main__':
    pass