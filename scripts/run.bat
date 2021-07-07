@SETLOCAL ENABLEDELAYEDEXPANSION
@SET ConEmuAnsi=OFF
@SET ConEmuHooks=OFF
@SET SDK_ARCH=%1
@SHIFT
@SET VSDevCmd=
@FOR /F "usebackq tokens=*" %%i in (`CALL "%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe" -version 16.0 -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -find Common7\Tools\VsDevCmd.bat -sort`) DO @(
	@SET "VSDevCmd=%%i"
)
@IF "%VSDevCmd%"=="" (
	@ECHO Failed to find VsDevCmd.bat for VisualStudio 2019
	@EXIT /B 1
)
@ECHO Using VsDevCmd.bat at "%VSDevCmd%"
@CALL "%VSDevCmd%" -no_logo -startdir=none -arch=%SDK_ARCH% -winsdk=10.0.17763.0
@IF ERRORLEVEL 1 EXIT /B !ERRORLEVEL!
CALL %1 %2 %3 %4 %5 %6 %7
@EXIT /B !ERRORLEVEL!
