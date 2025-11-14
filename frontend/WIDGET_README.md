# 🤖 Widget de Chatbot - Guía de Uso

## 📦 ¿Qué es el Widget?

El widget es una versión standalone del chatbot que puedes **embeber en cualquier página HTML** (WordPress, Shopify, HTML estático, etc.) sin necesidad de React o frameworks complejos.

---

## 🚀 Modo Desarrollo

### 1. Asegúrate de que el backend esté corriendo

```bash
cd backend
.venv\Scripts\activate
python -m uvicorn app.main:app --reload --port 8000
```

### 2. Iniciar el servidor del widget

En una terminal independiente:

```bash
cd frontend
npm run widget:dev
```

Esto inicia Vite en modo desarrollo en **http://localhost:5176**

### 3. Abrir la página de desarrollo

Abre en tu navegador:
```
http://localhost:5176/index-widget.html
```

**IMPORTANTE**: En modo desarrollo, NO uses `demo.html` directamente. Usa `index-widget.html` que carga el código TypeScript sin compilar.

---

## 🏗️ Modo Producción

### 1. Build del widget

```bash
cd frontend
npm run widget:build
```

Esto genera los archivos en `frontend/dist-widget/`:
- `widget.iife.js` - El script principal (todo incluido)
- `widget.css` - Los estilos CSS

### 2. Probar el build localmente

```bash
cd frontend
npm run widget:preview
```

Luego abre: `http://localhost:4173/demo.html`

### 3. Desplegar los archivos

Copia **ambos archivos** de `dist-widget/` a tu servidor web o CDN:
- `widget.iife.js`
- `widget.css`

### 4. Uso en producción

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Mi Sitio</title>
  <!-- Cargar estilos del widget -->
  <link rel="stylesheet" href="https://tu-cdn.com/widget.css">
</head>
<body>
  <h1>Bienvenido a mi sitio</h1>

  <!-- Widget del chatbot -->
  <div id="chatbot-widget-root"></div>
  <script src="https://tu-cdn.com/widget.iife.js"></script>
  <script>
    ChatbotWidget.init({
      botId: 'default',
      botName: 'Asistente Virtual',
      apiBaseUrl: 'https://tu-api.com',  // ⚠️ URL de producción
      primaryColor: '#3b82f6',
      position: 'bottom-right'
    });
  </script>
</body>
</html>
```

---

## ⚙️ Opciones de Configuración

| Opción | Tipo | Requerido | Default | Descripción |
|--------|------|-----------|---------|-------------|
| `botId` | string | ✅ | - | ID del bot a usar |
| `botName` | string | ❌ | "Asistente" | Nombre mostrado en el header |
| `apiBaseUrl` | string | ❌ | "http://localhost:8000" | URL del backend API |
| `primaryColor` | string | ❌ | "#3b82f6" | Color principal (HEX) |
| `position` | string | ❌ | "bottom-right" | Posición: "bottom-right" o "bottom-left" |

---

## 🎨 Ejemplos de Personalización

### Color verde (Éxito)
```javascript
ChatbotWidget.init({
  botId: 'default',
  botName: 'Soporte Técnico',
  primaryColor: '#10b981',  // Verde
  position: 'bottom-right'
});
```

### Color morado (Marca)
```javascript
ChatbotWidget.init({
  botId: 'ventas',
  botName: 'Asesor de Ventas',
  primaryColor: '#8b5cf6',  // Morado
  position: 'bottom-left'
});
```

### Bot específico con API personalizada
```javascript
ChatbotWidget.init({
  botId: 'soporte-tecnico',
  botName: 'IT Support',
  apiBaseUrl: 'https://api.miempresa.com',
  primaryColor: '#ef4444',  // Rojo
  position: 'bottom-right'
});
```

---

## 🌐 Integración en Diferentes Plataformas

### WordPress
1. Ve a **Apariencia → Editor de temas**
2. Edita `footer.php`
3. Pega el código del widget antes de `</body>`

### Shopify
1. Ve a **Temas → Acciones → Editar código**
2. Edita `theme.liquid`
3. Pega el código antes de `</body>`

### HTML Estático
Simplemente pega el código en tu archivo `.html`

### React/Next.js (si ya usas React)
Mejor usa el componente React directamente:
```tsx
import ChatWidget from './components/ChatWidget';

function App() {
  return (
    <ChatWidget
      botId="default"
      botName="Mi Bot"
      apiBaseUrl="https://api.example.com"
      primaryColor="#3b82f6"
      position="bottom-right"
    />
  );
}
```

---

## 🐛 Troubleshooting

### El widget no aparece
1. Verifica que el `<div id="chatbot-widget-root"></div>` exista
2. Revisa la consola del navegador (F12) en busca de errores
3. Confirma que `widget.js` se cargó correctamente

### "ChatbotWidget is not defined"
- El script `widget.js` no se cargó o hay un error de carga
- Verifica la URL del script en Network tab (F12)

### CORS Error
Si ves errores de CORS en la consola:

**Backend** - Agrega tu dominio a las CORS permitidas en `backend/app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://tu-sitio.com"],  # Agregar aquí
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### El chat no responde
1. Verifica que el backend esté corriendo
2. Confirma que `apiBaseUrl` apunta al backend correcto
3. Revisa que el `botId` existe en tu base de datos

---

## 📁 Estructura de Archivos

```
frontend/
├── src/
│   ├── widget-entry.tsx      # Punto de entrada del widget
│   └── components/
│       └── ChatWidget.tsx     # Componente principal
├── public/
│   └── demo.html              # Página de demostración
├── vite.widget.config.ts      # Configuración de Vite para widget
├── package.json               # Scripts: widget:dev, widget:build
└── dist-widget/               # Build final (generado)
    ├── widget.js              # Script principal
    └── widget.css             # Estilos
```

---

## 🎯 Siguiente Paso

**Para desarrollo**:
```bash
# Terminal 1 - Backend
cd backend
.venv\Scripts\activate
python -m uvicorn app.main:app --reload --port 8000

# Terminal 2 - Widget Dev Server
cd frontend
npm run widget:dev

# Abre: http://localhost:5176/index-widget.html
```

**Para producción**:
```bash
cd frontend
npm run widget:build

# Probar build localmente:
npm run widget:preview
# Abre: http://localhost:4173/demo.html

# Luego sube dist-widget/widget.iife.js y widget.css a tu CDN
```

---

## 💡 Notas Importantes

- ✅ El widget es **completamente standalone** - no depende del dashboard React
- ✅ Incluye **todas las dependencias** en un solo archivo JS
- ✅ Los estilos de Tailwind se compilan e incluyen automáticamente
- ✅ Funciona en **cualquier sitio web** (HTML, PHP, WordPress, etc.)
- ⚠️ Asegúrate de que el backend permita CORS desde el dominio donde embebas el widget
