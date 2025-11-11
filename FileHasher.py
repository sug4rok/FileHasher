# coding=utf-8
import argparse
from datetime import datetime
from importlib import import_module
from os import scandir, path, rename, getcwd
from sys import exit
from concurrent.futures import ThreadPoolExecutor, as_completed
from types import SimpleNamespace
import xlsxwriter

from FHFile import File
from FHResult import Result
from FHUtils import ASCII_TITLE


class NestedNamespace(SimpleNamespace):
    def __init__(self, dictionary, **kwargs):
        super().__init__(**kwargs)
        for key, value in dictionary.items():
            if isinstance(value, dict):
                self.__setattr__(key, NestedNamespace(value))
            else:
                self.__setattr__(key, value)


def iter_files(base_folder):
    '''
    Recursively traverses a folder, returning paths to all files.
    '''
    try:
        with scandir(base_folder) as entries:
            for entry in entries:
                if entry.is_dir(follow_symlinks=False):
                    yield from iter_files(entry.path)
                elif entry.is_file(follow_symlinks=False):
                    yield entry.path
    except PermissionError:
        return


def get_report_filename(scanning_folders, report_file):
    '''
    Generate a valid .xlsx report filename based on scan folders or
    user input.
    '''
    curr_dirname = getcwd()
    if not report_file:
        # Generate the report file name from the names of the
        # scanned folders
        report_file = []
        for scanfold in scanning_folders:
            report_file.append(path.basename(scanfold.rstrip('/\\')))
        report_file = path.join(curr_dirname, f'{'_'.join(report_file)}.xlsx')
    else:
        # Add current directory if path is not specified
        dirname = path.dirname(report_file)
        if not path.exists(dirname):
            dirname = curr_dirname
        # Make sure the extension is .xlsx
        report_file = path.splitext(report_file)[0] + '.xlsx'
        report_file = path.join(dirname, path.basename(report_file))

    # If the report file with the specified name already exists,
    # rename the old file by adding the date/time of its change
    # in the file name.
    if path.isfile(report_file):
        mtime = datetime.fromtimestamp(path.getmtime(report_file))
        mtime = mtime.strftime('%Y-%m-%d_%H%M%S')
        rename(report_file, f'{path.splitext(report_file)[0]}_{mtime}.xlsx')

    return report_file


def generate_report(report_filename, text, result, args):
    '''
    Generate an Excel report summarizing duplicate file results.
    '''
    with xlsxwriter.Workbook(report_filename) as workbook:
        # === Colors and styles ===
        colors = {'purple': '#D2D2FF', 'pink': '#FFCECE'}
        fmt = {
            'cap': workbook.add_format({
                'bold': True,
                'bg_color': colors['purple'],
                'align': 'center',
                'bottom': 1
             }),
            'cap_left': workbook.add_format({
                'bold': True,
                'bg_color': colors['purple'],
                'bottom': 7
            }),
            'data_cntr': workbook.add_format({
                'bg_color': colors['purple'],
                'align': 'center',
                'bottom': 7
            }),
            'data_cntr_light': workbook.add_format({
               'bg_color': colors['pink'],
               'align': 'center',
               'bottom': 7
            }),
            'data_left': workbook.add_format({
                'bg_color': colors['purple'],
                'bottom': 7
            }),
            'data_bold_cntr_light': workbook.add_format({
                'bold': True,
                'bg_color': colors['pink'],
                'align': 'center',
                'top': 1
            }),
        }

        # === Worksheets ===
        ws_detailed = workbook.add_worksheet(text.ws_detailed)
        ws_summary = workbook.add_worksheet(text.ws_summary)

        # === Details Sheet ===
        captions = (text.cap1_A1, text.cap1_B1, text.cap1_C1, text.cap1_D1,)
        if args.t:
            captions += (text.cap1_E1,)
        ws_detailed.write_row('A1', captions, fmt['cap'])

        for row, dup in enumerate(result.get_duplicates(), start=1):
            data = [
                result.get_orig_path_by_hash(dup.hash),
                dup.full_path,
                dup.hr_size,
                dup.hash,
                dup.ftype
            ]
            ws_detailed.write_row(row, 0, data)

        # === Summary Sheet ===
        captions = (text.cap2_A1, text.cap2_A2, text.cap2_A3,
                    text.cap2_A4, text.cap2_A5,)
        summary_values = [
            str(result.total_files),
            result.hr_total_size,
            str(result.redundancy_files),
            result.hr_redundancy_size,
            result.redundancy_percent
        ]
        ws_summary.write_column('A1', captions, fmt['cap_left'])
        ws_summary.write_column('B1', summary_values[:2], fmt['data_cntr'])
        ws_summary.write_column('B3', summary_values[2:],
                                fmt['data_cntr_light'])

        # === Top 10 Duplicates ===
        ws_summary.write('D1', text.cap3_D1, fmt['cap'])
        ws_summary.write('E1', text.cap3_E1, fmt['cap'])

        row = 1
        for file in result.get_top10_duplicates():
            ws_summary.write(row, 3, file.full_path, fmt['data_left'])
            ws_summary.write(row, 4, file.hr_size, fmt['data_cntr'])
            row += 1
        ws_summary.write(row, 4, result.get_top10_size(),
                         fmt['data_bold_cntr_light'])

        # === File Types (optional) ===
        if args.t:
            ws_summary.write('G1', text.cap4_G1, fmt['cap'])
            ws_summary.write('H1', text.cap4_H1, fmt['cap'])
            for row, file_types in enumerate(result.get_file_types(), start=1):
                ws_summary.write(row, 6, file_types[0], fmt['data_left'])
                ws_summary.write(row, 7, file_types[1], fmt['data_cntr'])

        # === Formatting ===
        ws_detailed.autofit()
        ws_detailed.set_column('A:B', 60)
        ws_detailed.freeze_panes('A2')
        ws_detailed.autofilter('A1:{}1'.format('E' if args.t else 'D'))
        if args.t:
            ws_detailed.set_column('E:E', 50)

        ws_summary.autofit()
        ws_summary.set_column('C:C', 2)
        ws_summary.set_column('D:D', 60)
        ws_summary.set_column('F:F', 2)
        if args.t:
            ws_summary.set_column('G:G', 50)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_help = False
    parser.formatter_class = argparse.RawTextHelpFormatter
    parser.description = f'''\n
{ASCII_TITLE}
=============================================================================
FileHasher 2.4.0

The program to search for duplicate files in a specified folder by their SHA1
or MD5 hashes.
=============================================================================
'''
    parser.epilog = u'''
Examples:

  > FileHasher --help

    Displays this help message.

  > FileHasher d:\\folder -r result.csv -a md5

    Scans the folder d:\\folder for duplicate files using the MD5 hash
    algorithm instead of the default SHA1.

    The results are saved to an Excel report file named result.xlsx
    (note: even if .csv is specified, the program automatically generates
    .xlsx format).

  > FileHasher \\\\shared\\folder -i 100 -t

    Scans the shared network folder \\shared\folder for duplicate files.

    The -i 100 option means that intermediate results will be shown every
    100 processed files.

    The -t option enables file type detection (e.g., "JPEG image data" or
    "Microsoft Word Document").

  > FileHasher d:\\folder1 \\\\shared\\folder2 -w 4

    Scans two folders simultaneously — one local (d:\\folder1) and one
    network (\\\\shared\\folder2) — for duplicate files using the default
    SHA1 hash algorithm.

    The report will automatically be saved as an Excel file named
    folder1_folder2.xlsx in the current working directory.
'''

    parser.add_argument('folder', metavar='FOLDER', type=str, nargs='+',
                        help='The path to the folder, including the name of\
 the folder\nitself. Several folders can be specified (see Examples)')
    parser.add_argument('-a', choices=['sha1', 'md5'], default='sha1',
                        help=u'Hash algorithm sha1 (default) or md5')
    parser.add_argument('-e', action='store_true',
                        help=u'Display advanced information such as memory\
consumption')
    parser.add_argument('-i', metavar='NUMBER', type=int, default=1000,
                        help=u'After how many scanned files an intermediate\
result should be\nshown')
    parser.add_argument('-l', choices=['en', 'ru'], default='en',
                        help=u'Language of output to the console and\
to the report file')
    parser.add_argument('-r', metavar='RESULT.XLSX', required=False, type=str,
                        help=u'Excel file with the result. If it was not\
specified, it is\ncreated in the program folder with the name of the scanned\
\nfolder')
    parser.add_argument('-t', action='store_true',
                        help=u'Detect file type, e.g. "Microsoft Excel 2007+"\
 or\n"ISO 9660 CD-ROM"')
    parser.add_argument('-w', metavar='WORKERS', type=int, default=2,
                        help=u'Maximum number of worker threads for file\
processing')

    args = parser.parse_args()
    iters = args.i
    if iters < 10 or iters > 10000:
        iters = 1000
    report_filename = get_report_filename(args.folder, args.r)

    text = NestedNamespace(import_module(f'locales.{args.l}').text)

    result = Result(text.cli, extend_info=args.e)
    result.print_result()

    all_files = []
    for sf in args.folder:
        for file_path in iter_files(sf):
            if not path.islink(file_path):
                all_files.append(file_path)

    def process_file(file_path):
        file = File(file_path, hash_alg=args.a, check_type=args.t)
        if file.size:
            file.set_file_data()
            result.add_file(file)

    with ThreadPoolExecutor(max_workers=args.w) as executor:
        futures = [executor.submit(process_file, fp) for fp in all_files]
        for i, future in enumerate(as_completed(futures), 1):
            if result.total_files % iters == 0:
                result.print_result()

    generate_report(report_filename, text.xls, result, args)

    result.print_result()
    print(f'\n {text.cli.done}!')
    print(f' {text.cli.report_created} {report_filename}')
