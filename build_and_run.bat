@echo off
set GCC="C:\Program Files (x86)\Dev-Cpp\MinGW64\bin\gcc.exe"
echo Compiling graphics_editor.c ...
%GCC% -std=c99 -Wall -O2 -o graphics_editor.exe graphics_editor.c -lm
if %ERRORLEVEL% EQU 0 (
    echo Compilation SUCCESS! Running...
    echo.
    graphics_editor.exe
) else (
    echo.
    echo Compilation FAILED. See errors above.
    pause
)
