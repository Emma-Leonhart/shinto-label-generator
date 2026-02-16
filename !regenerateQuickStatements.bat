@echo off
setlocal
cd /d "%~dp0"

cls
echo ==========================================
echo  Multi-Language QuickStatements Generator
echo  (Toki Pona, Korean, Chinese)
echo ==========================================
echo.

where py >nul 2>&1
if %errorlevel%==0 (
    set PYTHON=py -3
) else (
    set PYTHON=python
)

echo [1/3] Generating Toki Pona labels...
%PYTHON% fetch_shrines_tokiponize.py
if errorlevel 1 (
    echo.
    echo ERROR: Toki Pona pipeline failed.
    pause
    exit /b 1
)
echo.

echo [2/3] Generating Korean labels...
%PYTHON% generate_korean_quickstatements.py
if errorlevel 1 (
    echo.
    echo ERROR: Korean pipeline failed.
    pause
    exit /b 1
)
echo.

echo [3/3] Generating Chinese labels...
%PYTHON% generate_chinese_quickstatements.py
if errorlevel 1 (
    echo.
    echo ERROR: Chinese pipeline failed.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo  All pipelines complete!
echo  Output: quickstatements/tok.txt
echo          quickstatements/ko.txt
echo          quickstatements/zh.txt
echo ==========================================
exit /b 0
