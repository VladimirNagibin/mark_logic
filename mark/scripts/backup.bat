@echo off
set DATE=%DATE:~0,2%-%DATE:~3,2%-%DATE:~6,4%
set TIME=%TIME:~0,2%-%TIME:~3,2%
docker exec marklogic-db-1 pg_dump -U postgres -d mark > "d:\Mark Logic\pg_backups\backup_%DATE%_%TIME%.sql"
