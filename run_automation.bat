@echo off
echo ===============================================
echo   SIBBYRESPECT YOUTUBE AUTOMATION - LOCAL RUN
echo ===============================================
echo.
echo Starting video generation pipeline...
cd /d "%~dp0"
python main.py
echo.
echo ===============================================
echo   Task Finished! Check Output folder.
echo ===============================================
pause
