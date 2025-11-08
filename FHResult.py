# coding=utf-8
from os import system
from time import perf_counter

from FHFile import human_readable_size

ASCII_TITLE = r"""
  ___ _ _     _  _         _ 
 | __(_) |___| || |__ _ __| |_  ___ _ _
 | _|| | / -_) __ / _` (_-< ' \/ -_) '_|
 |_| |_|_\___|_||_\__,_/__/_||_\___|_|
"""


def human_readable_time(eval_time):
    """Convert seconds into a human-readable string (s, m, h, d)."""
    for unit, limit in (('s', 60.0), ('m', 60.0), ('h', 24.0)):
        if eval_time < limit:
            return f'{eval_time:.1f} {unit}'
        eval_time /= limit
    return f'{eval_time:.1f} d'


class Result:
    def __init__(self, text, iters=1000):
        self._start_time = perf_counter()
        self._originals = {}
        self._duplicates = {}
        self._text = text
        self._iters = iters

    def add_file(self, file):
        self._check_duplicate(file)
        if self.total_files % self._iters == 0:
            self.print_result()

    @property
    def total_files(self):
        return len(self._originals) + len(self._duplicates)

    @property
    def total_size(self):
        orig_size = sum([file.size for file in self._originals.values()])
        return orig_size + self.redundancy_size

    @property
    def hr_total_size(self):
        return human_readable_size(self.total_size)

    @property
    def redundancy_files(self):
        return len(self._duplicates)

    @property
    def redundancy_size(self):
        return sum([file.size for file in self._duplicates.values()])

    @property
    def hr_redundancy_size(self):
        return human_readable_size(self.redundancy_size)

    @property
    def redundancy_percent(self):
        if self.total_size:
            rp = round(100.0 * self.redundancy_size / self.total_size, 1)
            return f'{rp} %'
        return '0 %'

    def _check_duplicate(self, file):
        filehash = file.hash
        if filehash in self._originals:
            orig_file = self._originals[filehash]
            if orig_file.ctime is not None and file.ctime is not None:
                if orig_file.ctime < file.ctime:
                    self._duplicates[filehash] = file
                else:
                    self._duplicates[filehash] = orig_file
                    self._originals[filehash] = file
            else:
                self._duplicates[filehash] = file
        else:
            self._originals[filehash] = file

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

    def print_result(self):
        total_time = perf_counter() - self._start_time
        summary = {
            self._text.cli.total_files: self.total_files,
            self._text.cli.total_size: self.hr_total_size,
            self._text.cli.dup_files: self.redundancy_files,
            self._text.cli.dup_size: self.hr_redundancy_size,
            self._text.cli.dup_percent: self.redundancy_percent,
            self._text.cli.time_passed: human_readable_time(total_time),
        }

        captions_length = len(max(summary, key=len))
        system('cls')
        print(ASCII_TITLE)

        for caption, value in summary.items():
            print(f' {caption.ljust(captions_length)}: {value}')
