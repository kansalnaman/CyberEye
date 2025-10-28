@echo off
REM wait 10 sec so network & startup apps initialize
timeout /t 10 /nobreak >nul

cd /d "C:\Users\admin\Desktop\cyber_eye"
"C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe" cybereye_face.py
exit /b 0
