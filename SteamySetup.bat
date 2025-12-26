@echo off

reg Query "HKLM\Hardware\Description\System\CentralProcessor\0" | find /i "x86" > NUL && set OS=32BIT || set OS=64BIT

:: cd to script's directory in case Windows sets the working directory to something else
cd /D "%~dp0"

echo Python version:
py --version
echo:
echo NOTE: Python versions older than 3.12 might have compatability issues. Try installing a newer version of python if you cannot run the program properly.

if not %errorlevel%==0 (
  echo Could not find Python.
  echo Downloading installer from python.org, please wait...

  if %OS%==32BIT powershell -Command "Invoke-WebRequest https://www.python.org/ftp/python/3.12.6/python-3.12.6.exe -OutFile pyinstaller.exe"
  if %OS%==64BIT powershell -Command "Invoke-WebRequest https://www.python.org/ftp/python/3.12.6/python-3.12.6-amd64.exe -OutFile pyinstaller.exe"

  echo Done downloading executable.
  echo Please complete installation through the installer before continuing, make sure "Add Python to PATH" is checked.
  start %CD%\pyinstaller.exe
  pause

  py --version
  if not %errorlevel%==0 (
    echo Python still could not be found.
    pause
    exit
  )
)

echo pip version:
py -m pip --version
if not %errorlevel%==0 (
  echo Could not find pip.
  echo Installing pip with ensurepip...
  py -m ensurepip --upgrade

  py -m pip --version
  if not %errorlevel%==0 (
    echo pip still could not be found.
    pause
    exit
  )
)

echo Installing requirements...
py -m pip install -r requirements.txt
if not %errorlevel%==0 (
  echo Failed to install requirements.
  pause
  exit
)

pause
exit
