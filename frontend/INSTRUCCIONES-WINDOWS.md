# 🪟 Solución para Windows (PowerShell)

## ⚡ SOLUCIÓN RÁPIDA

### **Opción 1: Usar el archivo .bat (Más fácil)**

```powershell
# En PowerShell, ejecuta:
cd D:\2025\ChatBot\frontend
.\full-clean.bat
```

Luego:
```powershell
npm run dev
```

---

### **Opción 2: Comandos manuales en PowerShell**

```powershell
# 1. Ir a la carpeta del frontend
cd D:\2025\ChatBot\frontend

# 2. Detener procesos de Node (si hay alguno corriendo)
# Presiona Ctrl+C en la terminal donde corre npm run dev

# 3. Limpiar caché de Vite
Remove-Item -Path "node_modules\.vite" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path ".vite" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "dist" -Recurse -Force -ErrorAction SilentlyContinue

# 4. Limpiar caché de npm
npm cache clean --force

# 5. Eliminar node_modules y package-lock
Remove-Item -Path "node_modules" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "package-lock.json" -Force -ErrorAction SilentlyContinue

# 6. Reinstalar dependencias
npm install

# 7. Iniciar servidor
npm run dev
```

---

### **Opción 3: Comandos cortos (PowerShell)**

```powershell
# Todo en una línea:
Remove-Item node_modules\.vite,.vite,dist,node_modules,package-lock.json -Recurse -Force -ErrorAction SilentlyContinue; npm cache clean --force; npm install; npm run dev
```

---

## 🌐 Limpiar Caché del Navegador

Después de limpiar el proyecto, limpia el navegador:

### **Chrome/Edge:**
1. Presiona: `Ctrl + Shift + Delete`
2. Selecciona "Caché" e "Imágenes y archivos en caché"
3. Click en "Borrar datos"

### **O más rápido:**
- **Recarga forzada:** `Ctrl + Shift + R`
- **Modo incógnito:** `Ctrl + Shift + N`

---

## 📝 Pasos Completos (Paso a Paso)

### **1. Detener el servidor**
En la terminal donde corre `npm run dev`, presiona:
```
Ctrl + C
```

### **2. Ejecutar limpieza**
```powershell
cd D:\2025\ChatBot\frontend
.\full-clean.bat
```

### **3. Cerrar navegador**
- Cierra **todas** las ventanas del navegador
- No solo la pestaña, TODO el navegador

### **4. Iniciar servidor**
```powershell
npm run dev
```

### **5. Abrir en modo incógnito**
- **Chrome/Edge:** `Ctrl + Shift + N`
- **Firefox:** `Ctrl + Shift + P`

Ve a: `http://localhost:5176`

---

## 🔍 Si quieres matar manualmente procesos de Node

### **Ver procesos de Node:**
```powershell
Get-Process node -ErrorAction SilentlyContinue
```

### **Matar todos los procesos de Node:**
```powershell
Stop-Process -Name node -Force -ErrorAction SilentlyContinue
```

### **O usar Task Manager:**
1. `Ctrl + Shift + Esc`
2. Buscar "Node.js"
3. Click derecho → "Finalizar tarea"

---

## ✅ Resumen (Windows)

```powershell
# 1. Detener servidor
Ctrl + C

# 2. Limpiar proyecto
cd D:\2025\ChatBot\frontend
.\full-clean.bat

# 3. Cerrar navegador completamente

# 4. Iniciar servidor
npm run dev

# 5. Abrir en modo incógnito
Ctrl + Shift + N
→ http://localhost:5176
```

---

## 🚨 Alternativa: Usar Git Bash (si lo tienes instalado)

Si tienes Git Bash instalado, puedes usar los comandos de Linux:

```bash
# Abrir Git Bash en D:\2025\ChatBot\frontend
cd /d/2025/ChatBot/frontend
./full-clean.sh
npm run dev
```

---

## 📌 Comandos de PowerShell vs Linux

| Linux/Mac | Windows PowerShell |
|-----------|-------------------|
| `rm -rf` | `Remove-Item -Recurse -Force` |
| `pkill` | `Stop-Process` o `taskkill` |
| `./script.sh` | `.\script.bat` o `.\script.ps1` |

---

¡Con estos pasos el error debería solucionarse! 🚀
