@echo off
cd /d "%~dp0"
"C:\Users\hp\AppData\Local\Programs\Python\Python312\python.exe" scraper.py
start "" http://localhost:8000
"C:\Users\hp\AppData\Local\Programs\Python\Python312\python.exe" server.py
