# coding=utf-8
from math import floor, log

ASCII_TITLE = r'''
  ___ _ _     _  _         _
 | __(_) |___| || |__ _ __| |_  ___ _ _
 | _|| | / -_) __ / _` (_-< ' \/ -_) '_|
 |_| |_|_\___|_||_\__,_/__/_||_\___|_|
'''


def human_readable_time(eval_time):
    '''
    Convert seconds into a human-readable string (s, m, h, d).
    '''
    for unit, limit in (('s', 60.0), ('m', 60.0), ('h', 24.0)):
        if eval_time < limit:
            return f'{eval_time:.1f} {unit}'
        eval_time /= limit
    return f'{eval_time:.1f} d'


def human_readable_size(size):
    '''
    Convert a file size in bytes to a human-readable string.
    '''
    if size <= 0:
        return '0 B'

    units = ['B', 'kB', 'MB', 'GB', 'TB', 'PB']
    i = min(floor(log(size, 1024)), len(units) - 1)
    return f'{size / (1024 ** i):.1f} {units[i]}'
