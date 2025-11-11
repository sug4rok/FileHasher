# FileHasher

### The program to search for duplicate files in a specified folder by their SHA1 or MD5 hashes.

### Usage:

    FileHasher [-h] [-a {sha1,md5}] [-e] [-i NUMBER] [-l {en,ru}] [-r RESULT.XLSX] [-t] [-w WORKERS] FOLDER [FOLDER ...]

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
	-w WORKERS		Maximum number of worker threads for file processing

### Examples:

	> FileHasher --help

	  Displays this help message.

	> FileHasher d:\folder -r result.csv -a md5

	  Scans the folder d:\folder for duplicate files using the MD5 hash algorithm instead of the default SHA1.

	  The results are saved to an Excel report file named result.xlsx (note: even if .csv is specified, the program automatically generates
	  .xlsx format).

	> FileHasher \\shared\folder -i 100 -t

	  Scans the shared network folder \\shared\folder for duplicate files.

	  The -i 100 option means that intermediate results will be shown every 100 processed files.

	  The -t option enables file type detection (e.g., "JPEG image data" or "Microsoft Word Document").

	> FileHasher d:\folder1 \\shared\folder2 -w 4

	  Scans two folders simultaneously — one local (d:\folder1) and one network (\\shared\folder2) — for duplicate files using the default SHA1 hash algorithm.

	  The report will automatically be saved as an Excel file named folder1_folder2.xlsx in the current working directory.

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
