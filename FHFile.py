# coding=utf-8
from hashlib import sha1, md5
from os import stat

import magic


def human_readable_size(file_size):
    if file_size < 1024:
        return f'{file_size} B'
    file_size = round(file_size / 1024, 1)
    if 1024 > file_size >= 1:
        return f'{file_size} kB'
    file_size = round(file_size / 1024, 1)
    if 1024 > file_size >= 1:
        return f'{file_size} MB'
    file_size = round(file_size / 1024, 1)
    if 1024 > file_size >= 1:
        return f'{file_size} GB'
    return f'{round(file_size / 1024, 1)} TB'


class File:
    def __init__(self, full_file_path, hash_alg='sha1', define_type=False):
        self._full_file_path = full_file_path
        self._file_size = 0
        self._file_ctime = None
        self._file_type = None
        self._hash = None

        self._set_file_size()
        self._set_file_ctime()

        if hash_alg == 'sha1':
            self._hash_alg = sha1()
        else:
            self._hash_alg = md5()
        self._block_size = self._hash_alg.block_size * 1024
        self._set_file_hash()

        if define_type:
            self._set_file_type()

    @property
    def full_path(self):
        return self._full_file_path

    @property
    def size(self):
        return self._file_size

    @property
    def hr_size(self):
        return human_readable_size(self._file_size)

    def _set_file_size(self):
        try:
            self._file_size = stat(self._full_file_path).st_size
        except (FileNotFoundError, OSError):
            self._file_size = 0

    @property
    def ctime(self):
        return self._file_ctime

    def _set_file_ctime(self):
        try:
            self._file_ctime = stat(self._full_file_path).st_ctime
        except (FileNotFoundError, OSError):
            self._file_ctime = None

    @property
    def hash(self):
        return self._hash

    def _set_file_hash(self):
        try:
            with open(self._full_file_path, 'rb', buffering=0) as f:
                while chunk := f.read(self._block_size):
                    self._hash_alg.update(chunk)
        except (OSError, PermissionError):
            self._hash = None

        self._hash = self._hash_alg.hexdigest()

    @property
    def ftype(self):
        return self._file_type

    def _set_file_type(self):
        try:
            with open(self._full_file_path, 'rb', buffering=0) as f:
                try:
                    self._file_type = magic.from_buffer(f.read(2048))
                except magic.MagicException:
                    self._file_type = None
        except (OSError, PermissionError):
            self._file_type = None

    def __str__(self):
        return self.full_path
