@echo off
echo ========================================
echo  Push to GitHub - JobSpy Project
echo ========================================
echo.
echo Repository: https://github.com/Mostafa-SAID7/JobSpy
echo User: Mostafa-SAID7
echo.
echo You have 4 commits ready to push:
echo 1. Phase 4 - Dependency Injection Implementation
echo 2. Add deprecation warnings to old services
echo 3. Add final session summary
echo 4. Add GitHub push instructions
echo.
echo ========================================
echo  Pushing to GitHub...
echo ========================================
echo.

git push origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo  SUCCESS! Commits pushed to GitHub
    echo ========================================
    echo.
    echo Visit: https://github.com/Mostafa-SAID7/JobSpy/commits/main
    echo.
) else (
    echo.
    echo ========================================
    echo  FAILED - Authentication Required
    echo ========================================
    echo.
    echo Please use one of these methods:
    echo.
    echo 1. GitHub Desktop (Easiest):
    echo    Download: https://desktop.github.com/
    echo.
    echo 2. Personal Access Token:
    echo    Create at: https://github.com/settings/tokens
    echo    Then run: git push https://TOKEN@github.com/Mostafa-SAID7/JobSpy.git main
    echo.
    echo 3. GitHub CLI:
    echo    Install: winget install --id GitHub.cli
    echo    Then run: gh auth login
    echo.
)

pause
