#!/bin/bash

# Script para limpiar completamente el caché y reiniciar el proyecto

echo "🧹 Limpiando caché de Vite..."
rm -rf node_modules/.vite
rm -rf dist
rm -rf .vite

echo "🧹 Limpiando caché de npm..."
npm cache clean --force 2>/dev/null || true

echo "📦 Reinstalando dependencias..."
npm install

echo "✅ Limpieza completa!"
echo ""
echo "Para iniciar el proyecto:"
echo "  npm run dev"
