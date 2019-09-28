@ECHO OFF
SETLOCAL

SET ROOT=%CD%
SET ARCH=%~1
SET VIMVER=v%~2
SET VIMSRC=%~f3
SET BUILD=%~f4
CALL config.bat

IF NOT EXIST %BUILD%. MD %BUILD%

SET VIMSRC_BUILD=%BUILD%\vim\
SET XPM_x86=%VIMSRC_BUILD%src\xpm\x86
SET XPM_x64=%VIMSRC_BUILD%src\xpm\x64
SET XPM=!XPM_%ARCH%!

SET BUILDOPTIONS=CPU=%VIM_CPU% CVARS=/MP CPUNR=sse2 WINVER=0x501 ^
 DEBUG=no FEATURES=HUGE MBYTE=yes CSCOPE=yes ICONV=yes GETTEXT=yes ^
 TERMINAL=yes ^
 DYNAMIC_PERL=yes PERL="%PERL_DIR%" PERL_VER=%PERL_VER% ^
 DYNAMIC_LUA=yes LUA="%LUA_DIR%" LUA_VER=%LUA_VER% ^
 DYNAMIC_TCL=yes TCL="%TCL_DIR%" TCL_VER=%TCL_VER% TCL_VER_LONG=%TCL_VER_LONG% ^
 TCL_DLL=tcl86t.dll ^
 DYNAMIC_RUBY=yes RUBY="%RUBY_DIR%" RUBY_VER=%RUBY_VER% RUBY_VER_LONG=%RUBY_VER_LONG% ^
 RUBY_MSVCRT_NAME=msvcrt ^
 DYNAMIC_PYTHON=yes PYTHON="%PYTHON_DIR%" PYTHON_VER=%PYTHON_VER% ^
 DYNAMIC_PYTHON3=yes PYTHON3="%PYTHON3_DIR%" PYTHON3_VER=%PYTHON3_VER% ^
 DYNAMIC_MZSCHEME=yes "MZSCHEME=%RACKET_DIR%" MZSCHEME_VER=%MZSCHEME_VER% ^
 XPM="%XPM%"

IF EXIST "%VIMSRC_BUILD%" RD /Q /S %VIMSRC_BUILD%
git clone -q --shared %VIMSRC% %VIMSRC_BUILD% || EXIT /B 1

:: Incorporate patches
IF EXIST patch FOR %%i IN (%ROOT%\patch\*.patch) DO git -C %VIMSRC_BUILD% apply -v %%i
IF ERRORLEVEL 1 GOTO :EOF

PUSHD %VIMSRC_BUILD%src

PATH %PERL_DIR%\bin;%RUBY_DIR%\bin;%PATH%

ECHO ON

:: Build GVim
nmake -nologo -f Make_mvc.mak ^
 IME=yes GIME=yes GUI=yes OLE=yes DIRECTX=yes %BUILDOPTIONS% gvim.exe || EXIT /B 1

:: Build Vim
nmake -nologo -f Make_mvc.mak ^
 IME=no  GIME=no  GUI=no  OLE=no  DIRECTX=no  %BUILDOPTIONS% || EXIT /B 1
@ECHO OFF

PUSHD po
nmake -f Make_mvc.mak ^
 GETTEXT_PATH=%GETTEXT_DIR%\bin VIMRUNTIME=%VIMSRC_BUILD%\runtime ^
 install-all > NUL || EXIT /B 1
POPD

:: Build both 64- and 32-bit versions of gvimext.dll for the installer
IF NOT EXIST GvimExt64\. MKDIR GvimExt64
IF NOT EXIST GvimExt32\. MKDIR GvimExt32
START /B /WAIT CMD /C ""%VS140COMNTOOLS%\..\..\vc\vcvarsall.bat" x64 && CD GvimExt && nmake -nologo clean all" || EXIT /B 1
COPY /Y GvimExt\gvimext.dll  GvimExt\gvimext64.dll
MOVE /Y GvimExt\gvimext.dll  GvimExt64\gvimext.dll
COPY /Y GvimExt\README.txt   GvimExt64\
COPY /Y GvimExt\*.inf        GvimExt64\
COPY /Y GvimExt\*.reg        GvimExt64\
START /B /WAIT CMD /C ""%VS140COMNTOOLS%\..\..\vc\vcvarsall.bat" x86 && CD GvimExt && nmake -nologo clean all"  || EXIT /B 1
COPY /Y GvimExt\gvimext.dll GvimExt32\gvimext.dll
COPY /Y GvimExt\README.txt  GvimExt32\
COPY /Y GvimExt\*.inf       GvimExt32\
COPY /Y GvimExt\*.reg       GvimExt32\

@ECHO OFF
POPD

:: -----------------------------------------------------------------------

CD %VIMSRC_BUILD%src || EXIT /B 1

CALL :FindBinary 7z.exe "C:\Program Files\7-Zip" || EXIT /B

PATH %UPX_DIR%;%PATH%

C:\msys64\usr\bin\bash -lc ^
 "cd $(cygpath '%VIMSRC_BUILD%')/runtime/doc && touch ../../src/auto/config.mk && make uganda.nsis.txt"

ECHO ON
COPY /Y ..\README.txt ..\runtime\
COPY /Y ..\vimtutor.bat ..\runtime\
COPY /Y *.exe ..\runtime\
COPY /Y xxd\*.exe ..\runtime\
COPY /Y tee\*.exe ..\runtime\

MKDIR ..\runtime\GvimExt64
MKDIR ..\runtime\GvimExt32
COPY /Y GvimExt64\*.* ..\runtime\GvimExt64
COPY /Y GvimExt32\*.* ..\runtime\GvimExt32
COPY /Y %GETTEXT_DIR_x64%\bin\libiconv-2.dll      ..\runtime\GvimExt64 || EXIT /B 1
COPY /Y %GETTEXT_DIR_x64%\bin\libintl-8.dll       ..\runtime\GvimExt64 || EXIT /B 1
COPY /Y %GETTEXT_DIR_x86%\bin\libiconv-2.dll      ..\runtime\GvimExt32 || EXIT /B 1
COPY /Y %GETTEXT_DIR_x86%\bin\libintl-8.dll       ..\runtime\GvimExt32 || EXIT /B 1
COPY /Y %GETTEXT_DIR_x86%\bin\libgcc_s_sjlj-1.dll ..\runtime\GvimExt32 || EXIT /B 1

COPY /Y %GETTEXT_DIR%\bin\libiconv-2.dll ..\runtime\ || EXIT /B 1
COPY /Y %GETTEXT_DIR%\bin\libintl-8.dll  ..\runtime\ || EXIT /B 1
IF %ARCH% == x86 (
  COPY /Y %GETTEXT_DIR_x86%\bin\libgcc_s_sjlj-1.dll ..\runtime\ || EXIT /B 1
)

COPY /Y %LUA_DIR%\lua5.1.dll ..\runtime\lua51.dll || EXIT /B 1Z
IF %ARCH% == x86 COPY /Y %WINPTY_DIR%\%WINPTY_ARCH_x86%\bin\winpty.dll ..\runtime\winpty32.dll || EXIT /B 1
IF %ARCH% == x64 COPY /Y %WINPTY_DIR%\%WINPTY_ARCH_x64%\bin\winpty.dll ..\runtime\winpty64.dll || EXIT /B 1
COPY /Y %WINPTY_DIR%\%WINPTY_ARCH%\bin\winpty-agent.exe ..\runtime\ || EXIT /B 1
COPY /Y %ROOT%\extras\diff.exe ..\runtime\ || EXIT /B 1

SET dir=%BUILD%\vim-%VIMVER:v=%-%ARCH%
IF EXIST "%dir%" RD /Q /S "%dir%"
MKDIR %dir%
XCOPY ..\runtime %dir% /Y /E /V /I /H /R /Q
IF EXIST "%ROOT%\gvim-%VIMVER:v=%-%VIM_ARCH%.zip" DEL /F "%ROOT%\gvim-%VIMVER:v=%-%VIM_ARCH%.zip"
7z a "%ROOT%\gvim-%VIMVER:v=%-%VIM_ARCH%.zip" %dir%

COPY /Y %ROOT%\extras\diff.exe %VIMSRC_BUILD%\..
MKDIR %VIMSRC_BUILD%..\gettext64
MKDIR %VIMSRC_BUILD%..\gettext32
COPY /Y %GETTEXT_DIR_x86%\bin\libiconv-2.dll      %VIMSRC_BUILD%..\gettext32\ || EXIT /B 1
COPY /Y %GETTEXT_DIR_x86%\bin\libintl-8.dll       %VIMSRC_BUILD%..\gettext32\ || EXIT /B 1
COPY /Y %GETTEXT_DIR_x86%\bin\libgcc_s_sjlj-1.dll %VIMSRC_BUILD%..\gettext32\ || EXIT /B 1
COPY /Y %GETTEXT_DIR_x64%\bin\libiconv-2.dll      %VIMSRC_BUILD%..\gettext64\ || EXIT /B 1
COPY /Y %GETTEXT_DIR_x64%\bin\libintl-8.dll       %VIMSRC_BUILD%..\gettext64\ || EXIT /B 1
IF %ARCH% == x86 COPY /Y %WINPTY_DIR%\%WINPTY_ARCH_x86%\bin\winpty.dll %VIMSRC_BUILD%..\winpty32.dll
IF %ARCH% == x64 COPY /Y %WINPTY_DIR%\%WINPTY_ARCH_x64%\bin\winpty.dll %VIMSRC_BUILD%..\winpty64.dll
COPY /Y %WINPTY_DIR%\%WINPTY_ARCH%\bin\winpty-agent.exe %VIMSRC_BUILD%..
COPY /Y gvim.exe gvim_ole.exe
COPY /Y vim.exe vimw32.exe
COPY /Y xxd\xxd.exe xxdw32.exe
COPY /Y tee\tee.exe teew32.exe
COPY /Y install.exe installw32.exe
COPY /Y uninstall.exe uninstallw32.exe
PUSHD ..\nsis
7z x icons.zip -y
IF %ARCH% == x64 SET "NSIS_ARGS=/DWIN64"
"%NSIS_DIR%\makensis.exe" /DVIMRT=..\runtime /DGETTEXT=%VIMSRC_BUILD%.. ^
  %NSIS_ARGS% gvim.nsi ^
  "/XOutFile %ROOT%\gvim-%VIMVER:v=%-%VIM_ARCH%.exe"
POPD
@ECHO OFF
GOTO :EOF

:: -----------------------------------------------------------------------
:FindBinary
:: call :FindBinary <name> <defautlInstallPath>
IF "%~$PATH:1" == "" PATH %~2;%PATH%
GOTO :EOF
