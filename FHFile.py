# coding=utf-8
from hashlib import sha1, md5
from os import stat
import magic

from FHUtils import human_readable_size


class File:
    def __init__(self, full_file_path, hash_alg='sha1', check_type=False):
        self._full_file_path = full_file_path
        self._file_size = 0
        self._file_ctime = None
        self._file_type = None
        self._hash = None
        self._check_type = check_type

        self._set_file_size()
        self._set_file_ctime()

        if hash_alg == 'sha1':
            self._hash_alg = sha1()
        else:
            self._hash_alg = md5()
        self._block_size = self._hash_alg.block_size * 1024

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
        except OSError:
            self._file_size = 0

    @property
    def ctime(self):
        return self._file_ctime

    def _set_file_ctime(self):
        try:
            self._file_ctime = stat(self._full_file_path).st_ctime
        except OSError:
            self._file_ctime = None

    @property
    def hash(self):
        return self._hash

    @property
    def ftype(self):
        return self._file_type

    def _process_file(self):
        '''
        Compute hash and optionally detect file type in one file read.
        '''
        try:
            with open(self._full_file_path, 'rb') as f:
                # Read the initial header (enough for type detection)
                header = f.read(2048)

                # Detect file type if enabled
                if self._check_type:
                    try:
                        self._file_type = magic.from_buffer(header, mime=False)
                    except magic.MagicException:
                        self._file_type = None

                # Feed the header into the hash algorithm
                self._hash_alg.update(header)

                # Continue reading and hashing the rest of the file
                for chunk in iter(lambda: f.read(self._block_size), b''):
                    self._hash_alg.update(chunk)

            self._hash = self._hash_alg.hexdigest()

        except (OSError, ValueError):
            self._hash = None
            self._file_type = None

    def set_file_data(self):
        self._process_file()

    def __str__(self):
        return self.full_path
