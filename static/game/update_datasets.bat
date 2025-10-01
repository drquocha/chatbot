@echo off
echo 📚 Updating dataset list...
python update_datasets.py
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Python not found, trying python3...
    python3 update_datasets.py
)
echo.
echo ✅ Done! Refresh your browser to see new datasets.
pause