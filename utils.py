import os, errno, datetime

def ensure_dir_exists(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

# Calls os.path.join, but also ensures the directory exists
def join(*args):
    path = os.path.join(*args)
    ensure_dir_exists(os.path.dirname(path))
    return path

def datetime_mod(dt, divisor):
    n = int(dt.total_seconds() / divisor.total_seconds())
    return dt - n*divisor

def get_sidereal_time(dt):
    sidzero = datetime.datetime(2011,1,1)
    sidday = datetime.timedelta(hours=23.9344699)
    return datetime_mod(dt-sidzero, sidday)
