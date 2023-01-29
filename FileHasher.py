# coding=utf-8
import argparse
from datetime import datetime
from os import walk, path, rename
from sys import exit
import xlsxwriter

from FHFile import File
from FHResult import Result


def get_report_filename(scanning_folders, report_file):
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

    return report_file


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_help = False
    parser.formatter_class = argparse.RawDescriptionHelpFormatter
    parser.description = u"""\n
=====================================================================
FileHasher 2.0.2

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

    result = Result()
    result.print_result()

    for sf in args.folder:
        for root, dirs, files in walk(sf):
            for filename in files:
                file = File(path.join(root, filename),
                            hash_alg=args.a,
                            define_type=args.t)
                if file.size:
                    result.add_file(file)

                if result.total_files % args.i == 0:
                    result.print_result()

    originals = result.get_originals()
    duplicates = result.get_duplicates()

    report_filename = get_report_filename(args.folder, args.r)
    with xlsxwriter.Workbook(report_filename) as workbook:
        clr_purple = '#D2D2FF'
        clr_ping = '#FFCECE'
        stl_cap = workbook.add_format({
            'bold': True,
            'bg_color': clr_purple,
            'align': 'center',
            'bottom': 1,
        })
        stl_cap_left = workbook.add_format({
            'bold': True,
            'bg_color': clr_purple,
            'bottom': 7,
        })
        stl_data_cntr = workbook.add_format({
            'bg_color': clr_purple,
            'align': 'center',
            'bottom': 7,
        })
        stl_data_cntr_light = workbook.add_format({
            'bg_color': clr_ping,
            'align': 'center',
            'bottom': 7,
        })
        stl_data_left = workbook.add_format({
            'bg_color': clr_purple,
            'bottom': 7,
        })
        stl_data_bold_cntr_light = workbook.add_format({
            'bold': True,
            'bg_color': clr_ping,
            'align': 'center',
            'top': 1,
        })

        ws_detailed = workbook.add_worksheet(u'Подробно')
        ws_summary = workbook.add_worksheet(u'Итог')

        ws_detailed.set_column('A:B', 71)
        ws_detailed.set_column('C:C', 8)
        ws_detailed.set_column('D:D', 41)
        ws_detailed.autofilter('A1:D1')
        ws_detailed.freeze_panes('A2')

        # Table: Details
        captions = (
            'Оригинальный файл',
            'Дублирующий файл',
            'Размер',
            'Уникальный хэш файла',
        )
        if args.t:
            ws_detailed.set_column('E:E', 40)
            ws_detailed.autofilter('A1:E1')
            captions += ('Тип файла',)

        ws_detailed.write_row('A1', captions, stl_cap)
        for row, duplicate in enumerate(duplicates, 1):
            ws_detailed.write(row, 0, originals[duplicate.hash].full_path)
            ws_detailed.write(row, 1, duplicate.full_path)
            ws_detailed.write(row, 2, duplicate.hr_size)
            ws_detailed.write(row, 3, duplicate.hash)
            ws_detailed.write(row, 4, duplicate.ftype)

        ws_summary.set_column('A:A', 20)
        ws_summary.set_column('B:B', 8)
        ws_summary.set_column('C:C', 2)
        ws_summary.set_column('D:D', 71)
        ws_summary.set_column('E:E', 8)
        ws_summary.set_column('F:F', 2)

        # Table: Summary
        captions = (
            'Файлов всего',
            'Занято всего',
            'Дубликатов',
            'Занято дубликатами',
            'Процент дубликатов',
        )
        ws_summary.write_column('A1', captions, stl_cap_left)
        ws_summary.write(0, 1, f'{result.total_files}', stl_data_cntr)
        ws_summary.write(1, 1, result.hr_total_size, stl_data_cntr)
        ws_summary.write(2, 1, f'{result.redundancy_files}', stl_data_cntr_light)
        ws_summary.write(3, 1, result.hr_redundancy_size, stl_data_cntr_light)
        ws_summary.write(4, 1, result.redundancy_percent, stl_data_cntr_light)

        # Table: Top 10 Duplicates
        ws_summary.write(0, 3, 'Десятка самых больших дубликатов', stl_cap)
        ws_summary.write(0, 4, 'Размер', stl_cap)

        row = 1
        for file in result.get_top10_duplicates():
            ws_summary.write(row, 3, file.full_path, stl_data_left)
            ws_summary.write(row, 4, file.hr_size, stl_data_cntr)
            row += 1
        ws_summary.write(row, 4, result.get_top10_size(),
                         stl_data_bold_cntr_light)

        # Table: File Types
        if args.t:
            ws_summary.set_column('G:G', 60)
            ws_summary.set_column('H:H', 7)

            ws_summary.write(0, 6, 'Дублирующие файлы по типу', stl_cap)
            ws_summary.write(0, 7, 'Кол-во', stl_cap)
            for row, file_types in enumerate(result.get_file_types(), 1):
                ws_summary.write(row, 6, file_types[0], stl_data_left)
                ws_summary.write(row, 7, file_types[1], stl_data_cntr)

    result.print_result()
    print('\n DONE!')
