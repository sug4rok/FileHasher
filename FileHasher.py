# coding=utf-8
import argparse
from datetime import datetime
from importlib import import_module
from os import walk, path, rename
from sys import exit
from types import SimpleNamespace

import xlsxwriter
from FHFile import File
from FHResult import Result


class NestedNamespace(SimpleNamespace):
    def __init__(self, dictionary, **kwargs):
        super().__init__(**kwargs)
        for key, value in dictionary.items():
            if isinstance(value, dict):
                self.__setattr__(key, NestedNamespace(value))
            else:
                self.__setattr__(key, value)


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
    parser.description = """\n
=====================================================================
FileHasher 2.1.5

The program to search for duplicate files in a specified folder
by their SHA1 or MD5 hashes.
====================================================================="""
    parser.epilog = u"""
Examples:
  FileHasher --help
  FileHasher d:\\folder -r result.csv -a md5
  FileHasher \\\\shared\\folder -i 100 -t
  FileHasher d:\\folder1 \\\\shared\\folder2"""

    parser.add_argument('folder', metavar='FOLDER', type=str, nargs='+',
                        help='The path to the folder, including the name\
                        of the folder itself.\
                        Several folders can be specified (see Examples)')
    parser.add_argument('-a', choices=['sha1', 'md5'], default='sha1',
                        help=u'Hash algorithm sha1 (default) or md5')
    parser.add_argument('-i', metavar='NUMBER', type=int, default=1000,
                        help=u'After how many scanned files an intermediate\
                        result should be shown')
    parser.add_argument('-r', metavar='RESULT.XLSX', required=False, type=str,
                        help=u'Excel file with the result. If it was not\
                        specified, it is created in the program folder with\
                        the name of the scanned folder')
    parser.add_argument('-t', action='store_true',
                        help=u'Detect file type, e.g. "Microsoft Excel 2007+"\
                        or "ISO 9660 CD-ROM"')
    parser.add_argument('-l', choices=['en', 'ru'], default='ru',
                        help=u'Language of output to the console and\
                        to the report file')

    args = parser.parse_args()

    text = NestedNamespace(import_module(f'locales.{args.l}').text)

    result = Result(text)
    result.print_result()

    for sf in args.folder:
        for root, dirs, files in walk(sf, followlinks=False):
            for filename in files:
                file_path = path.join(root, filename)
                if path.islink(file_path):
                    continue
                file = File(file_path, hash_alg=args.a, check_type=args.t)
                if file.size:
                    file.set_file_data()
                    result.add_file(file)

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

        ws_detailed = workbook.add_worksheet(text.xls.ws_detailed)
        ws_summary = workbook.add_worksheet(text.xls.ws_summary)

        # Table: Details
        captions = (text.xls.cap1_A1, text.xls.cap1_B1,
                    text.xls.cap1_C1, text.xls.cap1_D1, )
        if args.t:
            captions += (text.xls.cap1_E1,)

        ws_detailed.write_row('A1', captions, stl_cap)
        for row, duplicate in enumerate(result.get_duplicates(), 1):
            orig_path = result.get_orig_path_by_hash(duplicate.hash)
            ws_detailed.write(row, 0, orig_path)
            ws_detailed.write(row, 1, duplicate.full_path)
            ws_detailed.write(row, 2, duplicate.hr_size)
            ws_detailed.write(row, 3, duplicate.hash)
            ws_detailed.write(row, 4, duplicate.ftype)

        # Table: Summary
        captions = (text.xls.cap2_A1, text.xls.cap2_A2, text.xls.cap2_A3,
                    text.xls.cap2_A4, text.xls.cap2_A5, )
        ws_summary.write_column('A1', captions, stl_cap_left)
        ws_summary.write(0, 1, f'{result.total_files}', stl_data_cntr)
        ws_summary.write(1, 1, result.hr_total_size, stl_data_cntr)
        ws_summary.write(2, 1, f'{result.redundancy_files}',
                         stl_data_cntr_light)
        ws_summary.write(3, 1, result.hr_redundancy_size, stl_data_cntr_light)
        ws_summary.write(4, 1, result.redundancy_percent, stl_data_cntr_light)

        # Table: Top 10 Duplicates
        ws_summary.write('D1', text.xls.cap3_D1, stl_cap)
        ws_summary.write('E1', text.xls.cap3_E1, stl_cap)

        row = 1
        for file in result.get_top10_duplicates():
            ws_summary.write(row, 3, file.full_path, stl_data_left)
            ws_summary.write(row, 4, file.hr_size, stl_data_cntr)
            row += 1
        ws_summary.write(row, 4, result.get_top10_size(),
                         stl_data_bold_cntr_light)

        # Table: File Types
        if args.t:
            ws_summary.write('G1', text.xls.cap4_G1, stl_cap)
            ws_summary.write('H1', text.xls.cap4_H1, stl_cap)
            for row, file_types in enumerate(result.get_file_types(), 1):
                ws_summary.write(row, 6, file_types[0], stl_data_left)
                ws_summary.write(row, 7, file_types[1], stl_data_cntr)

        ws_detailed.autofit()
        ws_detailed.set_column('A:B', 60)
        ws_detailed.freeze_panes('A2')
        ws_detailed.autofilter('A1:D1')
        if args.t:
            ws_detailed.set_column('E:E', 50)
            ws_detailed.autofilter('A1:E1')

        ws_summary.autofit()
        ws_summary.set_column('C:C', 2)
        ws_summary.set_column('D:D', 60)
        ws_summary.set_column('F:F', 2)
        if args.t:
            ws_summary.set_column('G:G', 50)

    result.print_result()
    print(f'\n {text.cli.done}!')
