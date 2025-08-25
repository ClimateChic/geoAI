@echo off
echo ClimateChic Boundary Analyzer
echo.
if "%~1"=="" (
    echo Usage: analyze.bat YOUR_FILE.geojson
    echo.
    echo Or drag and drop a .geojson file onto this script!
    pause
) else (
    python climatechic_mvp_poc.py "%~1"
    pause
)