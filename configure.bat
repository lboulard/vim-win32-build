@ECHO OFF
@SETLOCAL
IF "%APPVEYOR%" == "True" (
SET PACKAGES=packages.txt packages-appveyor.txt
) ELSE (
SET PACKAGES=packages.txt packages-python.txt
)
IF "%APPVEYOR_REPO_TAG%" == "true" (
SET VIMVER=%APPVEYOR_REPO_TAG_NAME%
) ELSE (
FOR /F "delims=" %%i in ('git describe --tags --abbrev^=0') DO SET VIMVER=%%i
)
@ECHO ON
python.exe scripts\configure.py ^
  --vim %VIMVER% ^
  --template-dir scripts ^
  --batch config.bat ^
  --ninja config.ninja ^
  %PACKAGES%
