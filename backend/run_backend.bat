@echo off
cd "c:\Users\karth\Documents\SEM7\SSC\cybervault\backend"
python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt
python scripts\seed.py
uvicorn app.main:app --host 0.0.0.0 --port 8000
