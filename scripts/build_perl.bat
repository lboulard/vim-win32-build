@SETLOCAL
@SET ARCH=%~1
@SET PERL_BUILD_DIR="%~f2"
@SET PERL_DIR="%~f3"
@IF EXIST "%PERL_DIR%" RD /Q /S "%PERL_DIR%"
@PUSHD %PERL_BUILD_DIR%\win32 || EXIT /B 1
@ECHO ON
SET ARGS=INST_TOP=%PERL_DIR% CCTYPE=MSVC141
IF "%ARCH%" == "x86" (
 SET ARGS=!ARGS! WIN64=undef
)
SET ARGS=!ARGS! -e "MAKE=nmake -nologo"
nmake -nologo -f Makefile %ARGS% || EXIT /B 1
nmake -nologo -f Makefile %ARGS% install || EXIT /B 1
@ECHO OFF
@POPD
