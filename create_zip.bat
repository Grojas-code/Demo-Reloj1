@echo off
powershell -Command "Compress-Archive -Path .\* -DestinationPath Reloj1.zip -Force"
echo Created Reloj1.zip
