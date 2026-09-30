@echo off
cd "c:\Users\karth\Documents\SEM&\SSC\cybervault\frontend"
if exist node_modules rmdir /s /q node_modules
if exist package-lock.json del /f /q package-lock.json
call npm install
call npm list vite @vitejs/plugin-react
