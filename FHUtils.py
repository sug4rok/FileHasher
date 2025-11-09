# coding=utf-8

ASCII_TITLE = r'''
  ___ _ _     _  _         _
 | __(_) |___| || |__ _ __| |_  ___ _ _
 | _|| | / -_) __ / _` (_-< ' \/ -_) '_|
 |_| |_|_\___|_||_\__,_/__/_||_\___|_|
'''


def human_readable_time(eval_time):
    '''Convert seconds into a human-readable string (s, m, h, d).'''
    for unit, limit in (('s', 60.0), ('m', 60.0), ('h', 24.0)):
        if eval_time < limit:
            return f'{eval_time:.1f} {unit}'
        eval_time /= limit
    return f'{eval_time:.1f} d'


def human_readable_size(file_size):
    '''Convert a file size in bytes to a human-readable string.'''
    if file_size < 1024:
        return f'{file_size} B'

    units = ['kB', 'MB', 'GB', 'TB', 'PB']
    for unit in units:
        file_size /= 1024.0
        if file_size < 1024:
            return f'{file_size:.1f} {unit}'
    return f'{file_size:.1f} {units[-1]}'
