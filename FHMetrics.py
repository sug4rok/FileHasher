# coding=utf-8
from psutil import Process, cpu_count
from time import perf_counter

from FHUtils import human_readable_time, human_readable_size


class Metrics:
    def __init__(self):
        self._start_time = perf_counter()
        self._process = Process()
        self._cpu_count = cpu_count(logical=True)

    @property
    def elapsed_time(self):
        return perf_counter() - self._start_time

    @property
    def hr_elapsed_time(self):
        return human_readable_time(self.elapsed_time)

    @property
    def num_threads(self):
        return self._process.num_threads()

    @property
    def mem_usage(self):
        return self._process.memory_info().rss

    @property
    def hr_mem_usage(self):
        return human_readable_size(self.mem_usage)

    @property
    def mem_usage_pct(self):
        return f'{self._process.memory_percent(memtype='rss'):.1f}'

    @property
    def cpu_usage_pct(self):
        return f'{self._process.cpu_percent() / self._cpu_count:.1f}'

    @property
    def read_bytes(self):
        return self._process.io_counters().read_bytes
