@SETLOCAL
@SET "TCL_BUILD_DIR=%~dp1"
@SET "TIMESTAMP=%~2"
@SET "TCL_DIR=%~dp2"

@IF EXIST "%TCL_DIR%" RD /Q /S %TCL_DIR%
@PUSHD %TCL_BUILD_DIR%\win || EXIT /B 1
@ECHO ON
nmake -nologo -f makefile.vc core shell dlls || EXIT /B
nmake -nologo -f makefile.vc install-binaries install-libraries INSTALLDIR=%TCL_DIR% || EXIT /B
@ECHO OFF
@TYPE NUL>"%TIMESTAMP%"
@POPD
