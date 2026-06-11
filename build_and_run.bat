@echo off
set GCC="C:\Users\manus\AppData\Local\Microsoft\WinGet\Packages\BrechtSanders.WinLibs.POSIX.UCRT_Microsoft.Winget.Source_8wekyb3d8bbwe\mingw64\bin\gcc.exe"
echo Compiling graphics_editor.c ...
%GCC% -std=c99 -Wall -Wextra -O2 -o graphics_editor.exe graphics_editor.c -lm
if %ERRORLEVEL% EQU 0 (
    echo Compilation SUCCESS! Running...
    echo.
    .\graphics_editor.exe
) else (
    echo.
    echo Compilation FAILED. See errors above.
    pause
)
