@echo off
REM Check if python is available
where python >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo Python was not found on your computer. Downloading and installing Python automatically...
    REM Download the latest Python installer (e.g., 3.12.3, adjust if you want a different version)
    powershell -Command "Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe -OutFile %TEMP%\python-installer.exe"
    REM Run the installer silently (no GUI, auto add to PATH)
    %TEMP%\python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    REM Delete installer after installation
    del %TEMP%\python-installer.exe
    echo Installation complete. Please restart Command Prompt if python is not detected yet.
    pause
    exit /b
) ELSE (
    echo Python detected. Running the script...
    python "%~dp0batchFile.py"
    pause
)
