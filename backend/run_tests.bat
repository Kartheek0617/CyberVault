@echo off
cd "c:\Users\karth\Documents\SEM7\SSC\cybervault\backend"
python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt
python tests\test_uuid_regression.py
