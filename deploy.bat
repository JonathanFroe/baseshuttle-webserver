@echo off

echo Downloading Data:
scp -r jonathan@jonathanfroehlich.de:/home/jonathan/baseshuttle-webserver/data %cd%
echo.
echo Uploading Data:
scp -r * jonathan@jonathanfroehlich.de:/home/jonathan/baseshuttle-webserver/
echo.
echo Restarting Service:
ssh -t jonathan@jonathanfroehlich.de "sudo systemctl restart baseshuttle-webserver"

timeout /T 10