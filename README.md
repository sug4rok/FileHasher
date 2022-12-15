# FileHasher
## Программа поиска дубликатов файлов в указанной папке по их SHA1- или MD5-хэшам.

### Запуск:
    FileHasher [-h] [-a {sha1,md5}] [-i NUMBER] [-r RESULT.XLSX] [-t] FOLDER [FOLDER ...]

### Позиционный аргумент:
    FOLDER          Путь к папке, включая имя самой папки. Папок может быть указано несколько (см. Примеры)

### Опциональные аргументы:
    -h, --help      Отображение данной справки  
    -a {sha1,md5}   Алгоритм хеширования sha1 (по умолчанию) или md5  
    -i NUMBER       Через какое кол-во проверенных файлов выводить промежуточный результат             
    -r RESULT.XLSX  Файл Excel с результатом. Если не указан, создается в папке с программой с именем сканируемой папки         
    -t              Определять тип файла, например, "Microsoft Excel 2007+" или "ISO 9660 CD-ROM"               

### Примеры:
    FileHasher --help
    FileHasher d:\folder -r result.csv -a md5
    FileHasher \\shared\folder -i 100 -t
    FileHasher d:\folder1 \\shared\folder2

### Зависимости:
- python-magic
- python-magic-bin
- XlsxWriter

### Скриншоты:
Процесс сканирования выполнен  
    
![Процесс сканирования](/Screenshots/Scanning_process.png "Процесс сканирования")

Лист Excel с подробным отчетом
    
![Подробный отчет](/Screenshots/report_detailed.png "Подробный отчет")

Лист Excel с суммарным отчетом  
    
![Сводный отчет](/Screenshots/report_summary.png "Сводный отчет")
