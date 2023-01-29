# coding=utf-8
from os import system
from time import time

from FHFile import human_readable_size

ASCII_TITLE = "  ___ _ _     _  _         _             \n" \
              " | __(_) |___| || |__ _ __| |_  ___ _ _  \n" \
              " | _|| | / -_) __ / _` (_-< ' \/ -_) '_| \n" \
              " |_| |_|_\___|_||_\__,_/__/_||_\___|_|   \n"


def human_readable_time(eval_time):
    eval_time = round(eval_time, 1)
    if eval_time < 60:
        return f'{eval_time} s'
    eval_time = round((eval_time / 60.0), 1)
    if 60 > eval_time >= 1:
        return f'{eval_time} m'
    return f'{round((eval_time / 60.0), 1)} h'


class Result:
    def __init__(self, text):
        self._start_time = time()
        self._files = []
        self._originals = {}
        self._duplicates = []
        self._text = text

    def add_file(self, file):
        self._files.append(file)
        self._check_duplicate(file)

    @property
    def total_files(self):
        return len(self._files)

    @property
    def total_size(self):
        return sum([file.size for file in self._files])

    @property
    def hr_total_size(self):
        return human_readable_size(self.total_size)

    @property
    def redundancy_files(self):
        return len(self._duplicates)

    @property
    def redundancy_size(self):
        return sum([file.size for file in self._duplicates])

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
        if file.hash in self._originals:
            orig_file = self._originals[file.hash]
            if orig_file.ctime < file.ctime:
                file.original = False
                self._duplicates.append(file)
            else:
                orig_file.original = False
                self._duplicates.append(orig_file)
                self._originals[file.hash] = file
        else:
            self._originals[file.hash] = file

    def get_originals(self):
        return self._originals

    def get_duplicates(self):
        return self._duplicates

    def get_top10_duplicates(self):
        return sorted(self._duplicates, key=lambda x: x.size, reverse=True)[:9]

    def get_top10_size(self):
        top10_size = sum([file.size for file in self.get_top10_duplicates()])
        return human_readable_size(top10_size)

    def get_file_types(self):
        file_types = {}
        for file in self._duplicates:
            file_types[file.ftype] = file_types.get(file.ftype, 0) + 1
        return sorted(file_types.items(), key=lambda x: x[1], reverse=True)

    def print_result(self):
        total_time = time() - self._start_time
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
