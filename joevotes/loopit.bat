set DISCORD_TOKEN=stuff
:start
start "" hideexec32.exe python joevotecount.py
SLEEP 300
taskkill /f /t /im hideexec32.exe
goto start
