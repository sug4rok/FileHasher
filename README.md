# FileHasher

### The program to search for duplicate files in a specified folder by their SHA1 or MD5 hashes.

### Usage:

    FileHasher [-h] [-a {sha1,md5}] [-i NUMBER] [-r RESULT.XLSX] [-t] [-l {en,ru}] FOLDER [FOLDER ...]

### Positional arguments:

    FOLDER          The path to the folder, including the name of the folder itself. Several folders can be specified (see Examples)

### Options:

	-h, --help      show this help message and exit
	-a {sha1,md5}   Hash algorithm sha1 (default) or md5
	-e              Display advanced information such as memory consumption
	-i NUMBER       After how many scanned files an intermediate result should be shown
	-l {en,ru}      Language of output to the console and to the report file
	-r RESULT.XLSX  Excel file with the result. If it was not specified, it is created in the program folder with the name of the scanned folder
	-t              Detect file type, e.g. "Microsoft Excel 2007+" or "ISO 9660 CD-ROM"

### Examples:

    FileHasher --help
    FileHasher d:\folder -r result.xlsx -a md5
    FileHasher \\shared\folder -i 100 -t
    FileHasher d:\folder1 \\shared\folder2 e:\folder3 -e

### Dependencies:

- python-magic
- python-magic-bin
- XlsxWriter

### Screenshots:

Scan completed

![Процесс сканирования](/Screenshots/scan_process.png "Scan process")

Excel sheet with detailed report

![Detailed report](/Screenshots/report_detailed.png "Detailed report")

Excel sheet with summary report

![Summary report](/Screenshots/report_summary.png "Summary report")
