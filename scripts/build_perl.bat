@SETLOCAL
@CALL config.bat
@PATH %DMAKE_DIR%;%PATH%
@SET ARCH=%~1
@SET PERL_BUILD_DIR="%~f2"
@SET PERL_DIR="%~f3"
@IF EXIST "%PERL_DIR%" RD /Q /S "%PERL_DIR%"
@PUSHD %PERL_BUILD_DIR%\win32
@IF ERRORLEVEL 1 EXIT /B 1
@ECHO ON
SET ARGS=INST_TOP=%PERL_DIR% CCTYPE=MSVC141
IF "%ARCH%" == "x86" (
 SET ARGS=!ARGS! WIN64=undef
)
@REM Next line avoid a bug with setargv.obj in VS2017/Windows 10
SET ARGS=!ARGS! CFG=DebugFull
dmake -P%NUMBER_OF_PROCESSORS% -f makefile.mk %ARGS% all installbare || EXIT /B 1
@ECHO OFF
@POPD
