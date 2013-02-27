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

sidday = datetime.timedelta(hours=23.9344699)

def timedelta_as_time(td):
    return datetime.time(td.seconds/3600, td.seconds/60%60, td.seconds%60, td.microseconds)

def get_sidereal_time(dt):
    global sidday
    sidzero = datetime.datetime(2011,1,1)
    return datetime_mod(dt-sidzero, sidday)

