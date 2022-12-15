# coding=utf-8
import argparse
import hashlib
from datetime import datetime
from os import walk, stat, path, rename, system
from sys import exit
from time import time

import magic
import xlsxwriter

ASCII_TITLE = "  ___ _ _     _  _         _             \n" \
              " | __(_) |___| || |__ _ __| |_  ___ _ _  \n" \
              " | _|| | / -_) __ / _` (_-< ' \/ -_) '_| \n" \
              " |_| |_|_\___|_||_\__,_/__/_||_\___|_|   \n"
COLOR_PURPLE = '#D2D2FF'
COLOR_PINK = '#FFCECE'

start_time = time()
permission_denied = 0
unicode_decode_err = 0
magic_err = 0
other_err = 0
total_files = 0
total_size = 0
redundancy_files = 0
redundancy_size = 0
file_types = {}


def get_hash_from_file(full_file_path, hash_alg, block_size):
    global permission_denied

    try:
        with open(full_file_path, 'rb', buffering=0) as f:
            while chunk := f.read(block_size):
                hash_alg.update(chunk)

    except PermissionError:
        permission_denied += 1
        return None
    except OSError:
        other_err += 1
        return None

    return hash_alg.hexdigest()


def redundancy_percent():
    if total_size:
        return f'{round(100.0 * redundancy_size / total_size, 1)} %'
    return '0 %'


def file_size_dimension(file_size):
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


def elapsed_time_dimension(total_time):
    total_time = round(total_time, 1)
    if total_time < 60:
        return f'{total_time} s'
    total_time = round((total_time / 60.0), 1)
    if 60 > total_time >= 1:
        return f'{total_time} m'
    return f'{round((total_time / 60.0), 1)} h'


def print_result():
    total_time = time() - start_time
    results = {
        'Total files': total_files,
        'Total size': file_size_dimension(total_size),
        'Redundancy files': redundancy_files,
        'Redundancy size': file_size_dimension(redundancy_size),
        'Redundancy percentage': redundancy_percent(),
        'Permission denied errors': permission_denied,
        'Unicode decode errors': unicode_decode_err,
        'File type identification errors': magic_err,
        'Other errors': other_err,
        'Time passed': elapsed_time_dimension(total_time),
    }

    captions_length = len(max(results, key=len))
    system('cls')
    print(ASCII_TITLE)

    for caption, value in results.items():
        print(f' {caption.ljust(captions_length)}: {value}')


def get_workbook(scanning_folders, report_file):
    if report_file is None:
        report_file = []
        for sf in scanning_folders:
            report_file.append(path.basename(sf.rstrip('\\').rstrip('/')))
        report_file = f'.\\{"_".join(report_file)}.xlsx'
    else:
        if not path.dirname(report_file):
            report_file = path.join('.', report_file)

        if not path.exists(path.dirname(report_file)):
            print(f'\nFolder {path.dirname(report_file)} does not exist\n')
            exit()

    rp_name, rp_ext = path.splitext(report_file)
    if rp_ext != '.xlsx':
        rp_ext = '.xlsx'
        report_file = rp_name + rp_ext

    # If the report file with the specified name already exists,
    # rename the old file by adding the date/time of its change
    # in the file name.
    if path.isfile(report_file):
        rp_modified = datetime.fromtimestamp(path.getmtime(report_file))
        rp_modified = rp_modified.strftime('%Y-%m-%d_%H%M%S')
        rename(report_file, f'{rp_name}_{rp_modified}{rp_ext}')

    return xlsxwriter.Workbook(report_file)


def get_ws_detailed(workbook, find_file_type):
    worksheet = workbook.add_worksheet(u'Подробно')
    style_cap = workbook.add_format()
    style_cap.set_bg_color(COLOR_PURPLE)
    style_cap.set_bold(True)
    style_cap.set_align('center')
    style_cap.set_bottom(1)
    worksheet.set_column(0, 1, 71)
    worksheet.set_column(2, 2, 8)
    worksheet.set_column(3, 3, 41)
    worksheet.autofilter(0, 0, 0, 3)

    captions = (
        'Оригинальный файл',
        'Дублирующий файл',
        'Размер',
        'Уникальный хэш файла',
    )
    if find_file_type:
        worksheet.set_column(4, 4, 40)
        worksheet.autofilter(0, 0, 0, 4)
        captions += ('Тип файла',)

    for caption in captions:
        worksheet.write(0, captions.index(caption), caption, style_cap)

    return worksheet


def add_ws_summary(workbook, find_file_type):
    worksheet = workbook.add_worksheet(u'Итог')
    style_cap_cntr = workbook.add_format()
    style_cap_cntr.set_bg_color(COLOR_PURPLE)
    style_cap_cntr.set_bold(True)
    style_cap_cntr.set_align('center')
    style_cap_cntr.set_bottom(1)
    style_cap_left = workbook.add_format()
    style_cap_left.set_bg_color(COLOR_PURPLE)
    style_cap_left.set_bold(True)
    style_cap_left.set_bottom(7)
    style_data_cntr = workbook.add_format()
    style_data_cntr.set_bg_color(COLOR_PURPLE)
    style_data_cntr.set_align('center')
    style_data_cntr.set_bottom(7)
    style_data_cntr_light = workbook.add_format()
    style_data_cntr_light.set_bg_color(COLOR_PINK)
    style_data_cntr_light.set_align('center')
    style_data_cntr_light.set_bottom(7)
    style_data_left = workbook.add_format()
    style_data_left.set_bg_color(COLOR_PURPLE)
    style_data_left.set_bottom(7)
    style_data_bold_cntr_light = workbook.add_format()
    style_data_bold_cntr_light.set_bg_color(COLOR_PINK)
    style_data_bold_cntr_light.set_align('center')
    style_data_bold_cntr_light.set_top(1)
    style_data_bold_cntr_light.set_bold(True)
    worksheet.set_column(0, 0, 20)
    worksheet.set_column(1, 1, 8)
    worksheet.set_column(2, 2, 2)
    worksheet.set_column(3, 3, 71)
    worksheet.set_column(4, 4, 8)
    worksheet.set_column(5, 5, 2)

    # Table Summary
    worksheet.write(0, 0, 'Файлов всего', style_cap_left)
    worksheet.write(0, 1, f'{total_files}', style_data_cntr)

    worksheet.write(1, 0, 'Занято всего', style_cap_left)
    worksheet.write(1, 1, file_size_dimension(total_size), style_data_cntr)

    worksheet.write(2, 0, 'Дубликатов', style_cap_left)
    worksheet.write(2, 1, f'{redundancy_files}', style_data_cntr_light)

    worksheet.write(3, 0, 'Занято дубликатами', style_cap_left)
    worksheet.write(3, 1, file_size_dimension(redundancy_size),
                    style_data_cntr_light)

    worksheet.write(4, 0, 'Процент дубликатов', style_cap_left)
    worksheet.write(4, 1, redundancy_percent(), style_data_cntr_light)

    # Table Top 10 Duplicates
    worksheet.write(0, 3, 'Десятка самых больших дубликатов', style_cap_cntr)
    worksheet.write(0, 4, 'Размер', style_cap_cntr)
    row = 1
    duplicates_sorted = sorted(duplicate_files.items(),
                               key=lambda x: x[1], reverse=True)
    top10_size = 0
    for f_path, f_size in duplicates_sorted[0:9]:
        worksheet.write(row, 3, f_path, style_data_left)
        worksheet.write(row, 4, file_size_dimension(f_size), style_data_cntr)
        top10_size += f_size
        row += 1
    worksheet.write(row, 4, file_size_dimension(top10_size),
                    style_data_bold_cntr_light)

    # Table File Types
    if find_file_type:
        worksheet.set_column(6, 6, 60)
        worksheet.set_column(7, 7, 7)

        worksheet.write(0, 6, 'Дублирующие файлы по типу', style_cap_cntr)
        worksheet.write(0, 7, 'Кол-во', style_cap_cntr)
        row = 1
        sorted_file_types = sorted(file_types.items(), key=lambda x: x[1],
                                   reverse=True)
        for file_type, num in sorted_file_types:
            worksheet.write(row, 6, file_type, style_data_left)
            worksheet.write(row, 7, num, style_data_cntr)
            row += 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_help = False
    parser.formatter_class = argparse.RawDescriptionHelpFormatter
    parser.description = u"""\n
=====================================================================
FileHasher 1.8.0

Программа поиска дубликатов файлов в указанной папке по их SHA1- или
MD5-хэшам.
====================================================================="""
    parser.epilog = u"""
Примеры:
  FileHasher --help
  FileHasher d:\\folder -r result.csv -a md5
  FileHasher \\\\shared\\folder -i 100 -t
  FileHasher d:\\folder1 \\\\shared\\folder2"""

    parser.add_argument('folder', metavar='FOLDER', type=str, nargs='+',
                        help=u'Путь к папке, включая имя самой папки.\
                        Папок может быть указано несколько (см. Примеры)')
    parser.add_argument('-a', choices=['sha1', 'md5'], default='sha1',
                        help=u'Алгоритм хеширования sha1 (по умолчанию)\
                        или md5')
    parser.add_argument('-i', metavar='NUMBER', type=int, default=1000,
                        help=u'Через какое кол-во проверенных файлов выводить \
                        промежуточный результат')
    parser.add_argument('-r', metavar='RESULT.XLSX', required=False, type=str,
                        help=u'Файл Excel с результатом. Если не указан,\
                        создается в папке с программой с именем\
                        сканируемой папки')
    parser.add_argument('-t', action='store_true',
                        help=u'Определять тип файла, например,\
                        "Microsoft Excel 2007+" или "ISO 9660 CD-ROM"')

    args = parser.parse_args()

    scanning_folders = args.folder

    if args.a == 'sha1':
        hash_alg = hashlib.sha1()
    else:
        hash_alg = hashlib.md5()
    block_size = hash_alg.block_size * 1024
    iterations = args.i
    report_file = args.r
    find_file_type = args.t

    original_file = {}
    duplicate_files = {}
    workbook = get_workbook(scanning_folders, report_file)
    worksheet_detailed = get_ws_detailed(workbook, find_file_type)

    print_result()

    row = 1
    for sf in scanning_folders:
        for root, dirs, files in walk(sf, followlinks=False):
            for file in files:
                full_file_path = path.join(root, file)
                total_files += 1
                try:
                    file_size = stat(full_file_path).st_size
                except (FileNotFoundError, OSError) as e:
                    other_err += 1
                    continue

                # Skipping empty files
                if not file_size:
                    continue

                total_size += file_size

                file_hash = get_hash_from_file(full_file_path, hash_alg.copy(),
                                               block_size)
                if file_hash is None:
                    continue

                # If we already have the same hash, we consider this file is
                # a duplicate file
                if file_hash in original_file:
                    redundancy_files += 1
                    redundancy_size += file_size
                    duplicate_files[full_file_path] = file_size

                    try:
                        duplicate_row = (original_file[file_hash],
                                         full_file_path,
                                         file_size_dimension(file_size),
                                         file_hash)

                        if find_file_type:
                            with open(full_file_path, 'rb', buffering=0) as f:
                                try:
                                    ft = magic.from_buffer(f.read(2048))
                                except magic.magic.MagicException:
                                    magic_err += 1
                                duplicate_row += (ft,)
                                file_types[ft] = file_types.get(ft, 0) + 1

                        for item in duplicate_row:
                            worksheet_detailed.write(row,
                                                     duplicate_row.index(item),
                                                     item)

                        row += 1
                    except UnicodeEncodeError:
                        unicode_decode_err += 1
                else:
                    original_file[file_hash] = full_file_path

                if total_files % iterations == 0:
                    print_result()

    add_ws_summary(workbook, find_file_type)
    workbook.close()
    print_result()
    print('\n DONE!')
