del dtv_associations.parquet couples_clubs_federations.db resultParser.log
python -OO sqlitedatabase.py
python -OO dtvprocessing.py
C:\Users\EBELIN_B\bin\SQlite\sqlite-tools-win-x64-3460100\sqlite3.exe -markdown couples_clubs_federations.db "select * from Fed_Club_Count;"