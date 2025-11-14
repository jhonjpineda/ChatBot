#!/bin/bash

echo "🛑 LIMPIEZA COMPLETA DEL PROYECTO"
echo "================================="
echo ""

# 1. Matar cualquier proceso de Vite/npm corriendo
echo "1️⃣ Deteniendo procesos de desarrollo..."
pkill -f "vite" 2>/dev/null || true
pkill -f "npm run dev" 2>/dev/null || true
sleep 2

# 2. Limpiar cachés de Vite
echo "2️⃣ Limpiando caché de Vite..."
rm -rf node_modules/.vite
rm -rf .vite
rm -rf dist

# 3. Limpiar caché de npm
echo "3️⃣ Limpiando caché de npm..."
npm cache clean --force 2>/dev/null || true

# 4. Eliminar node_modules y package-lock
echo "4️⃣ Eliminando node_modules..."
rm -rf node_modules
rm -f package-lock.json

# 5. Reinstalar dependencias
echo "5️⃣ Reinstalando dependencias..."
npm install

echo ""
echo "✅ LIMPIEZA COMPLETA!"
echo ""
echo "📝 IMPORTANTE:"
echo "  1. Cierra COMPLETAMENTE tu navegador"
echo "  2. Abre el navegador de nuevo"
echo "  3. Ejecuta: npm run dev"
echo "  4. Abre en modo incógnito si persiste el error"
echo ""
