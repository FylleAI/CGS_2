@echo off
echo Installing frontend dependencies...
set "PATH=%PATH%;C:\Program Files\nodejs"
cd onboarding-frontend
npm install
echo.
echo Installation complete!
pause

