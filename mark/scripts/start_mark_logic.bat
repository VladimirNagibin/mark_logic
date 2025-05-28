@echo off
timeout /t 40 /nobreak > nul
docker compose -f docker-compose.production.yml up -d
exit
