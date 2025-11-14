# 🔧 Solución Error de Caché de Vite

## ❌ Error:
```
Uncaught SyntaxError: The requested module '/src/types/index.ts'
does not provide an export named 'RegisterRequest' (at Users.tsx:5:26)
```

## 🎯 Causa:
Este error ocurre por **caché persistente de Vite**. El archivo SÍ tiene las exportaciones correctas, pero Vite usa una versión cacheada antigua.

---

## ✅ SOLUCIÓN COMPLETA (Paso a Paso)

### **Paso 1: Detener el servidor**
```bash
# En la terminal donde corre npm run dev, presiona:
Ctrl + C
```

### **Paso 2: Ejecutar limpieza completa**
```bash
cd frontend
./full-clean.sh
```

**O manualmente:**
```bash
cd frontend

# Limpiar cachés
rm -rf node_modules/.vite
rm -rf .vite
rm -rf dist
rm -rf node_modules
rm -f package-lock.json

# Limpiar caché de npm
npm cache clean --force

# Reinstalar
npm install
```

### **Paso 3: Limpiar navegador**
**IMPORTANTE:** Debes limpiar el caché del navegador también.

**Opción A - Recarga Forzada (Rápida):**
- **Chrome/Edge/Firefox:** `Ctrl + Shift + R` (Windows/Linux)
- **Mac:** `Cmd + Shift + R`

**Opción B - Limpiar Caché Completo:**
- **Chrome/Edge:**
  1. `Ctrl + Shift + Delete`
  2. Seleccionar "Caché" e "Imágenes y archivos en caché"
  3. Limpiar

**Opción C - Modo Incógnito (Más Fácil):**
- **Chrome/Edge:** `Ctrl + Shift + N`
- **Firefox:** `Ctrl + Shift + P`

### **Paso 4: Reiniciar el servidor**
```bash
npm run dev
```

### **Paso 5: Abrir en el navegador**
```bash
# Si ya estaba abierto, CIERRA LA PESTAÑA y abre una nueva
http://localhost:5176
```

---

## 🚨 Si TODAVÍA sigue el error:

### **Opción 1: Reiniciar TODO**
```bash
# 1. Cerrar COMPLETAMENTE el navegador (todas las ventanas)
# 2. Cerrar terminal
# 3. Abrir nueva terminal
cd frontend
./full-clean.sh
npm run dev
# 4. Abrir navegador en modo incógnito
```

### **Opción 2: Verificar puerto**
```bash
# A veces el puerto 5176 queda ocupado
# Verifica que no haya otro proceso corriendo:
lsof -i :5176

# Si hay algo, mátalo:
kill -9 <PID>
```

### **Opción 3: Usar otro navegador**
Si Chrome tiene el problema, prueba con:
- Firefox
- Edge
- Brave

### **Opción 4: Verificar que los archivos están actualizados**
```bash
cd frontend/src/types
cat index.ts | grep -A 5 "RegisterRequest"
```

Deberías ver:
```typescript
export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
  role?: UserRole;
  organization_id?: string;
  allowed_bots?: string[];
}
```

---

## 📝 Prevención Futura

Para evitar este error en el futuro:

### **1. Siempre usar imports consistentes:**
```typescript
// ✅ SIEMPRE así:
import { User } from '../types/index';

// ❌ NUNCA así:
import { User } from '../types';
```

### **2. Limpiar caché regularmente:**
```bash
# Antes de cada sesión de desarrollo:
cd frontend
rm -rf node_modules/.vite .vite dist
npm run dev
```

### **3. Script rápido:**
Agrega a `package.json`:
```json
{
  "scripts": {
    "dev": "vite",
    "dev:clean": "rm -rf node_modules/.vite .vite dist && vite"
  }
}
```

Luego usa:
```bash
npm run dev:clean
```

---

## 🎯 Resumen

**El problema NO es el código** (las exportaciones están correctas).
**El problema ES el caché** (Vite guarda versiones antiguas).

**Solución:**
1. ✅ Ejecutar `./full-clean.sh`
2. ✅ Cerrar navegador completamente
3. ✅ Iniciar servidor con `npm run dev`
4. ✅ Abrir en modo incógnito

**Si nada funciona:**
- Reinicia tu computadora
- Usa otro navegador
- Contacta con más detalles del error

---

## 🆘 Información de Debug

Si sigues teniendo el problema, ejecuta estos comandos y comparte el output:

```bash
# 1. Versión de Node
node --version

# 2. Versión de npm
npm --version

# 3. Verificar archivo types
cat src/types/index.ts | grep -A 3 "export interface RegisterRequest"

# 4. Verificar imports en Users.tsx
head -10 src/pages/Users.tsx

# 5. Verificar caché de Vite
ls -la node_modules/.vite 2>/dev/null || echo "No cache"

# 6. Procesos corriendo en puerto 5176
lsof -i :5176 || echo "Puerto libre"
```

---

**¿Funcionó?** Si después de estos pasos sigue el error, es posible que sea un problema diferente. Comparte:
- Sistema operativo
- Versión de Node/npm
- Output de los comandos de debug arriba
