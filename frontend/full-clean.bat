@echo off
REM Script de limpieza completa para Windows

echo.
echo ============================================
echo  LIMPIEZA COMPLETA DEL PROYECTO
echo ============================================
echo.

REM 1. Detener procesos de Node/Vite
echo [1/6] Deteniendo procesos de desarrollo...
taskkill /F /IM node.exe 2>nul
timeout /t 2 /nobreak >nul

REM 2. Limpiar caché de Vite
echo [2/6] Limpiando cache de Vite...
if exist node_modules\.vite rmdir /s /q node_modules\.vite
if exist .vite rmdir /s /q .vite
if exist dist rmdir /s /q dist

REM 3. Limpiar caché de npm
echo [3/6] Limpiando cache de npm...
call npm cache clean --force

REM 4. Eliminar node_modules y package-lock
echo [4/6] Eliminando node_modules...
if exist node_modules rmdir /s /q node_modules
if exist package-lock.json del /f /q package-lock.json

REM 5. Reinstalar dependencias
echo [5/6] Reinstalando dependencias...
call npm install

echo.
echo [6/6] LIMPIEZA COMPLETA!
echo.
echo IMPORTANTE:
echo   1. Cierra COMPLETAMENTE tu navegador
echo   2. Abre el navegador de nuevo
echo   3. Ejecuta: npm run dev
echo   4. Abre en modo incognito si persiste el error
echo.
pause
