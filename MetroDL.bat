@echo off
setlocal EnableDelayedExpansion

echo --- MetroDL Started ---
SET "PYDIR="
SET "FFDIR="

IF NOT EXIST .venv (
    echo --- SETUP ---
    REM creation of conf file with path to ffmpeg and python (leave empty to use default)
    SET "PYDIR=python"
    SET /P "PYDIR=Path to Python binary (leave empty to use system):"
    IF "!PYDIR!"=="" (
        SET "PYDIR=python"
    )

    SET "FFDIR=ffmpeg"
    SET /P "FFDIR=Path to FFMPEG binary (leave empty to try use system, you MUST have configured the enviroment varible!):"
    IF "!FFDIR!"=="" (
        SET "FFDIR=ffmpeg"
    )

    echo --- Writing config file ---
    echo SET PYDIR=!PYDIR!> .paths.conf
    echo SET FFDIR=!FFDIR!>> .paths.conf

    echo --- Creating venv ---
    !PYDIR! -m venv .venv
    call .venv\Scripts\activate.bat

    echo --- Installing dependencies ---
    pip install -r requirements.txt
) ELSE (
    cmd /c .paths.conf
    call .venv\Scripts\activate.bat
)

%PYDIR% MetroDL.py -f %FFDIR% %*
endlocal
pause
