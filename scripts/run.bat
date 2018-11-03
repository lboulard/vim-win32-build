@SET ConEmuAnsi=OFF
@SET ConEmuHooks=OFF
@SET SDK_ARCH=%1
@SHIFT
@SET VS2017InstallDir=
@CALL :GetVS2017InstallDir32 HKLM >NUL 2>&1
@IF ERRORLEVEL 1 CALL :GetVS2017InstallDir32 HKCU >NUL 2>&1
@IF ERRORLEVEL 1 CALL :GetVS2017InstallDir64 HKLM >NUL 2>&1
@IF ERRORLEVEL 1 CALL :GetVS2017InstallDir64 HKCU >NUL 2>&1
@IF "%VS2017InstallDir%"=="" (
	@ECHO Failed to find VisualStudio 2017
	@EXIT /B 1
)
@ECHO Using VisualStudio 2017 at "%VS2017InstallDir%"
@CALL "%VS2017InstallDir%\Common7\Tools\vsdevcmd.bat" -no_logo -startdir=none ^
    -arch=%SDK_ARCH% -winsdk=10.0.17763.0
@IF ERRORLEVEL 1 EXIT /B 1
CALL %1 %2 %3 %4 %5 %6 %7
@IF ERRORLEVEL 1 EXIT /B 1
@EXIT /B 0

:GetVS2017InstallDir32
@FOR /F "tokens=1,2*" %%i IN ('reg query "%1\SOFTWARE\Microsoft\VisualStudio\SxS\VS7" /v "15.0"') DO (
	@IF "%%i"=="15.0" (
		@SET VS2017InstallDir=%%k
	)
)
@IF "%VS2017InstallDir%"=="" EXIT /B 1
@EXIT /B 0

:GetVS2017InstallDir64
@FOR /F "tokens=1,2*" %%i IN ('reg query "%1\SOFTWARE\Wow6432Node\Microsoft\VisualStudio\SxS\VS7" /v "15.0"') DO (
	@IF "%%i"=="15.0" (
		@SET VS2017InstallDir=%%k
	)
)
@IF "%VS2017InstallDir%"=="" EXIT /B 1
@EXIT /B 0
