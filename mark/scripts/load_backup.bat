@echo off
docker exec marklogic-db-1 bash -c "dropdb -U postgres --if-exists mark"
if %errorlevel% neq 0 (
  echo Error dropping database
  exit /b 1
)

docker exec marklogic-db-1 bash -c "createdb -U postgres mark"
if %errorlevel% neq 0 (
  echo Error creating database
  exit /b 1
)

docker exec marklogic-db-1 bash -c "psql -U postgres -d mark -f /backups/backup_25-05-2025_21-11.sql"
if %errorlevel% neq 0 (
  echo Error restoring backup
  exit /b 1
)

echo Restore completed successfully
pause
