@SETLOCAL
@SET TCL_DIR="%~f2"
@SET TCL_BUILD_DIR="%~f1"
@IF EXIST "%TCL_DIR%" RD /Q /S %TCL_DIR%
@PUSHD %TCL_BUILD_DIR%\win || EXIT /B 1
@ECHO ON
nmake -nologo -f makefile.vc core shell dlls || EXIT /B
nmake -nologo -f makefile.vc install-binaries install-libraries INSTALLDIR=%TCL_DIR% || EXIT /B
@ECHO OFF
@POPD
