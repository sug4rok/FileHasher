# coding=utf-8
from sys import getsizeof
from os import system
from time import perf_counter

from FHUtils import ASCII_TITLE, human_readable_time, human_readable_size


class Result:
    def __init__(self, text, iters=1000, extend_info=False):
        self._start_time = perf_counter()
        self._total_files = 0
        self._total_size = 0
        self._originals = {}
        self._duplicates = {}
        self._text = text.cli
        self._iters = iters
        self._extend_info = extend_info

        self._summary_keys = [
            'total_files',
            'total_size',
            'dup_files',
            'dup_size',
            'dup_percent',
            'time_passed',
        ]
        if self._extend_info:
            self._summary_keys.extend([
                'mem_orig_size',
                'mem_dup_size',
            ])
        captions = [getattr(self._text, key) for key in self._summary_keys]
        self._max_caption = len(max(captions, key=len))

    def add_file(self, file):
        self._total_files += 1
        self._total_size += file.size
        self._check_duplicate(file)
        if self._total_files % self._iters == 0:
            self.print_result()

    @property
    def total_files(self):
        return self._total_files

    @property
    def hr_total_size(self):
        return human_readable_size(self._total_size)

    @property
    def redundancy_files(self):
        return len(self._duplicates)

    @property
    def redundancy_size(self):
        return sum(file.size for file in self._duplicates.values())

    @property
    def hr_redundancy_size(self):
        return human_readable_size(self.redundancy_size)

    @property
    def redundancy_percent(self):
        if not self._total_size:
            return '0 %'
        return f'{(100.0 * self.redundancy_size / self._total_size):.1f} %'

    def _check_duplicate(self, file):
        '''
        Check whether a file is a duplicate and update the originals/duplicates
        dictionaries.
        '''
        filehash = file.hash
        orig_file = self._originals.get(filehash)

        # If this is the first file with this hash, store it as an original
        if orig_file is None:
            self._originals[filehash] = file
            return

        # If both files have creation times, choose the older one as
        # the original
        if orig_file.ctime and file.ctime:
            if file.ctime < orig_file.ctime:
                self._duplicates[filehash] = orig_file
                self._originals[filehash] = file
            else:
                self._duplicates[filehash] = file
            return

        # If the creation time is unknown, we simply treat the new file as
        # a duplicate.
        self._duplicates[filehash] = file

    def get_originals(self):
        return self._originals.values()

    def get_duplicates(self):
        return self._duplicates.values()

    def get_orig_path_by_hash(self, filehash):
        return self._originals[filehash].full_path

    def get_top10_duplicates(self):
        return sorted(self.get_duplicates(),
                      key=lambda x: x.size, reverse=True)[:9]

    def get_top10_size(self):
        top10_size = sum([file.size for file in self.get_top10_duplicates()])
        return human_readable_size(top10_size)

    def get_file_types(self):
        file_types = {}
        for file in self.get_duplicates():
            file_types[file.ftype] = file_types.get(file.ftype, 0) + 1
        return sorted(file_types.items(), key=lambda x: x[1], reverse=True)

    @property
    def mem_orig_size(self):
        return human_readable_size(getsizeof(self._originals))

    @property
    def mem_dup_size(self):
        return human_readable_size(getsizeof(self._duplicates))

    def print_result(self):
        '''
        Print a formatted summary of the current results.
        '''
        system('cls')
        print(ASCII_TITLE)

        total_time = human_readable_time(perf_counter() - self._start_time)

        summary = [
            (self._text.total_files, self.total_files),
            (self._text.total_size, self.hr_total_size),
            (self._text.dup_files, self.redundancy_files),
            (self._text.dup_size, self.hr_redundancy_size),
            (self._text.dup_percent, self.redundancy_percent),
            (self._text.time_passed, total_time),
        ]

        if self._extend_info:
            summary.extend([
                (f'[ {self._text.mem_usage_title} ]', None),
                (self._text.mem_orig_size, self.mem_orig_size),
                (self._text.mem_dup_size, self.mem_dup_size),
            ])

        for caption, value in summary:
            if value is None:
                print(f' {caption}')
            else:
                print(f' {caption.ljust(self._max_caption)}: {value}')
