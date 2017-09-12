@ECHO OFF
SETLOCAL /ENABLEDELAYEDEXPANSION /ENABLEEXTENSIONS
SET ARCH=%~1
SET RUBY_BUILD_DIR="%~f2"
SET RUBY_DIR="%~f3"
SET RUBY_VER_LONG=%~4
SET RUBY_VERSION=%~5
SET RUBY_ARCH_x86=i386-mswin32
SET RUBY_ARCH_x64=x64-mswin64
SET RUBY_ARCH=!RUBY_ARCH_%ARCH%!

IF EXIST "%RUBY_DIR%" @RD /Q /S "%RUBY_DIR%
PUSHD %RUBY_BUILD_DIR%
ECHO ON
CALL win32\configure.bat --target=%RUBY_ARCH% ^
  --disable-install-doc ^
  --without-ext "socket,fiddle,openssl,curses,pty,readline,dbm,gdbm,fcntl,tk,syslog" ^
  --disable-rubygems ^
  --disable-debug-env ^
  --prefix=$(RUBY_DIR) || EXIT /B
nmake -nologo -l || EXIT /B
nmake -nologo install-nodoc || EXIT /B
XCOPY /I /Y /S .ext\include %RUBY_DIR%\include\ruby-%RUBY_VER_LONG% || EXIT /B
@ECHO OFF
POPD
