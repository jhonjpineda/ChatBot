# 📚 Guía de Uso - ChatBot RAG Multi-Tenant

Esta guía te mostrará paso a paso cómo usar el sistema de chatbots RAG.

## 📋 Tabla de Contenidos

1. [Iniciar el Sistema](#iniciar-el-sistema)
2. [Crear un Nuevo Bot](#crear-un-nuevo-bot)
3. [Subir Documentos](#subir-documentos)
4. [Probar el Chat](#probar-el-chat)
5. [Embeber el Widget en tu Sitio Web](#embeber-el-widget)
6. [Ver Analytics](#ver-analytics)

---

## 🚀 Iniciar el Sistema

### 1. Iniciar el Backend (FastAPI)

```bash
cd backend
.venv\Scripts\activate  # En Windows
# o
source .venv/bin/activate  # En Linux/Mac

# Luego ejecutar
python -m uvicorn app.main:app --reload --port 8000
```

El backend estará disponible en: **http://localhost:8000**

### 2. Iniciar el Frontend (React)

En otra terminal:

```bash
cd frontend
npm run dev
```

El frontend estará disponible en: **http://localhost:5176**

---

## 🤖 Crear un Nuevo Bot

### Paso 1: Acceder a la Sección de Bots

1. Abre el navegador en `http://localhost:5176`
2. En el menú lateral, haz clic en **"Bots"** (icono 🤖)

### Paso 2: Crear el Bot

1. Haz clic en el botón **"Crear Nuevo Bot"**
2. Completa el formulario:

   **Campos Obligatorios:**
   - **bot_id**: Identificador único (sin espacios, ej: `soporte-ventas`)
   - **name**: Nombre descriptivo (ej: `Bot de Soporte Ventas`)

   **Campos Opcionales:**
   - **description**: Descripción del bot (ej: `Bot para atender consultas de ventas`)
   - **system_prompt**: Puedes elegir un preset o escribir uno personalizado

   **Presets disponibles:**
   - `general`: Asistente virtual general
   - `customer_support`: Soporte al cliente
   - `technical_support`: Soporte técnico
   - `sales`: Asistente de ventas
   - `educational`: Tutor educativo
   - `medical`: Asistente médico

   **Configuración Avanzada:**
   - **temperature**: Control de creatividad (0.0 - 2.0)
     - `0.0 - 0.3`: Respuestas precisas y determinísticas
     - `0.4 - 0.7`: Balance (recomendado: 0.7)
     - `0.8 - 2.0`: Más creativo y variado

   - **retrieval_k**: Número de fragmentos a recuperar (1-20)
     - `4`: Valor por defecto recomendado
     - `6-8`: Para contexto más amplio
     - `1-3`: Para respuestas más enfocadas

3. Haz clic en **"Crear Bot"**

### Ejemplo de Bot:

```
bot_id: soporte-tecnico
name: Bot de Soporte Técnico
description: Asistente para resolver dudas técnicas de productos
system_prompt: [Seleccionar preset "technical_support"]
temperature: 0.7
retrieval_k: 6
```

---

## 📄 Subir Documentos

### Paso 1: Ir a la Sección de Documentos

1. En el menú lateral, haz clic en **"Documentos"** (icono 📄)

### Paso 2: Seleccionar el Bot

1. En el selector superior, elige el bot al que quieres asociar los documentos
   - Cada bot solo tendrá acceso a sus propios documentos

### Paso 3: Subir Archivos

**Opción A: Arrastrar y Soltar**
1. Arrastra uno o varios archivos al área de carga
2. Los archivos se subirán automáticamente

**Opción B: Seleccionar Archivos**
1. Haz clic en **"Haz clic para seleccionar"**
2. Selecciona uno o más archivos
3. Los archivos se subirán automáticamente

**Formatos Soportados:**
- PDF (`.pdf`)
- Word (`.docx`)
- Texto plano (`.txt`)

### Paso 4: Verificar la Carga

Los documentos aparecerán en la tabla inferior mostrando:
- Nombre del archivo
- ID del documento
- Bot asociado
- Número de chunks (fragmentos indexados)
- Fecha de carga

**Nota:** El sistema divide automáticamente los documentos en fragmentos (chunks) de ~800 caracteres con overlap de 100 caracteres para mejorar la recuperación de información.

---

## 💬 Probar el Chat

### Opción 1: Usar el Widget de Demo

1. Ve a la sección **"Chat Widget"** (icono 💬) en el menú
2. Selecciona el bot que quieres probar
3. Haz clic en **"Mostrar Widget"**
4. Un widget flotante aparecerá en la esquina inferior derecha
5. Escribe tu pregunta y presiona Enter o haz clic en enviar

### Opción 2: Probar desde el Dashboard

1. Ve al **Dashboard** (inicio)
2. En la sección de bots, haz clic en un bot
3. Aparecerá un chat de prueba

---

## 🌐 Embeber el Widget en tu Sitio Web

### ⚠️ Limitación Actual

El archivo `widget.js` **no está implementado aún**. Por ahora solo puedes usar el widget dentro de aplicaciones React.

### Uso en Aplicaciones React

1. Copia el componente `ChatWidget` de `frontend/src/components/ChatWidget.tsx`
2. En tu aplicación React, impórtalo:

```jsx
import ChatWidget from './components/ChatWidget';

function App() {
  return (
    <div>
      {/* Tu contenido */}

      <ChatWidget
        botId="soporte-tecnico"
        botName="Bot de Soporte Técnico"
        apiBaseUrl="http://localhost:8000"
        primaryColor="#3b82f6"
        position="bottom-right"
      />
    </div>
  );
}
```

### Configuración del Widget

**Propiedades disponibles:**

| Propiedad | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `botId` | string | ✅ Sí | ID único del bot |
| `botName` | string | ❌ No | Nombre del bot (default: "Asistente") |
| `apiBaseUrl` | string | ❌ No | URL del backend (default: "http://localhost:8000") |
| `primaryColor` | string | ❌ No | Color hexadecimal (default: "#3b82f6") |
| `position` | string | ❌ No | "bottom-right" o "bottom-left" (default: "bottom-right") |

---

## 📊 Ver Analytics

### Paso 1: Acceder a Analytics

1. En el menú lateral, haz clic en **"Analytics"** (icono 📈)

### Paso 2: Filtrar Datos

1. **Seleccionar Bot**: Elige un bot específico o "Todos los bots (Global)"
2. **Rango de Tiempo**: Actualmente muestra todos los datos (filtro en desarrollo)

### Métricas Disponibles

**Tarjetas Principales:**
- **Total Interacciones**: Número total de conversaciones
- **Tasa de Éxito**: Porcentaje de respuestas exitosas
  - 🟢 Verde: ≥90% (Excelente)
  - 🟡 Amarillo: 70-89% (Bueno)
  - 🔴 Rojo: <70% (Requiere atención)
- **Tiempo Promedio**: Tiempo de respuesta promedio (con min/max)
- **Total Errores**: Número de errores ocurridos

**Desglose Diario:**
- Tabla con estadísticas por día:
  - Fecha
  - Interacciones
  - Éxitos vs Errores
  - Tasa de éxito
  - Tiempo promedio de respuesta

**Preguntas Más Frecuentes:**
- Top 10 preguntas más realizadas
- Contador de veces preguntada
- Bot asociado

---

## 🎯 Buenas Prácticas

### Para Crear Bots

1. **IDs descriptivos**: Usa nombres claros como `soporte-ventas` en lugar de `bot1`
2. **Prompts específicos**: Define claramente el rol del bot en el system_prompt
3. **Temperature adecuada**:
   - Usa 0.3-0.5 para información factual (soporte técnico)
   - Usa 0.7-1.0 para conversaciones más naturales
4. **Retrieval_k apropiado**:
   - Empieza con 4 y ajusta según necesites
   - Aumenta si las respuestas carecen de contexto
   - Disminuye si las respuestas son muy largas o confusas

### Para Documentos

1. **Organiza por bot**: Sube documentos relevantes solo al bot que los necesita
2. **Formato adecuado**:
   - PDF para manuales y documentos oficiales
   - DOCX para documentos editables
   - TXT para datos simples
3. **Nombres descriptivos**: Usa nombres de archivo claros
4. **Actualiza regularmente**: Elimina documentos obsoletos

### Para Embedimiento

1. **CORS**: Asegúrate de configurar CORS en el backend si usas desde otro dominio
2. **Colores**: Usa colores que coincidan con tu marca
3. **Posición**: Elige la posición que no interfiera con tu UI

---

## 🐛 Solución de Problemas

### El chat no responde

**Posibles causas:**
1. ✅ Verifica que el bot exista y esté activo
2. ✅ Asegúrate de que el bot tenga documentos indexados
3. ✅ Revisa que Ollama esté ejecutándose (si usas Ollama)
4. ✅ Verifica que el modelo esté descargado (`ollama pull llama3.2:1b`)

### No puedo subir documentos

**Posibles causas:**
1. ✅ Verifica el formato del archivo (PDF, DOCX, TXT)
2. ✅ Comprueba que el archivo no esté corrupto
3. ✅ Revisa los logs del backend para errores específicos

### El widget no aparece

**Posibles causas:**
1. ✅ El archivo `widget.js` no existe (usa el componente React directamente)
2. ✅ Verifica que el `botId` sea correcto
3. ✅ Asegúrate de que el backend esté corriendo

### Error 422 en el chat

**Solución aplicada:**
- El servicio de chat ha sido corregido para enviar `{ question, bot_id }` correctamente

---

## 📞 Estructura de la API

### Endpoints Principales

**Bots:**
- `GET /bots/` - Listar bots
- `POST /bots/` - Crear bot
- `GET /bots/{bot_id}` - Obtener bot
- `PUT /bots/{bot_id}` - Actualizar bot
- `DELETE /bots/{bot_id}` - Eliminar bot
- `GET /bots/presets/prompts` - Obtener presets

**Documentos:**
- `POST /documents/upload?bot_id=xxx` - Subir documento
- `GET /documents/list?bot_id=xxx` - Listar documentos
- `DELETE /documents/{doc_id}` - Eliminar documento

**Chat:**
- `POST /chat/` - Enviar mensaje
  ```json
  {
    "question": "¿Cómo funciona X?",
    "bot_id": "soporte-tecnico"
  }
  ```

**Analytics:**
- `GET /analytics/bot/{bot_id}` - Analytics de un bot
- `GET /analytics/global` - Analytics globales
- `GET /analytics/popular-questions?bot_id=xxx&limit=10` - Preguntas frecuentes

---

## 🔧 Configuración Avanzada

### Variables de Entorno (backend/.env)

```bash
APP_NAME=Chatbot RAG
APP_ENV=development
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:1b
```

### Cambiar de Ollama a OpenAI

1. Modifica el `.env`:
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=tu-api-key-aqui
OPENAI_MODEL=gpt-3.5-turbo
```

2. Reinicia el backend

---

## ✅ Checklist de Inicio Rápido

- [ ] Backend ejecutándose en puerto 8000
- [ ] Frontend ejecutándose en puerto 5176
- [ ] Ollama ejecutándose (si usas Ollama)
- [ ] Modelo descargado (`ollama pull llama3.2:1b`)
- [ ] Bot creado con ID único
- [ ] Documentos subidos e indexados
- [ ] Chat probado y funcionando
- [ ] Analytics mostrando datos

---

## 📝 Notas Adicionales

- Los bots con `bot_id="default"` no pueden eliminarse desde la UI
- Los documentos se procesan automáticamente al subirlos
- El chunking con overlap mejora la calidad de las respuestas
- Las analytics se actualizan en tiempo real
- Cada bot es completamente independiente (multi-tenant)

---

**¿Necesitas más ayuda?** Revisa los logs del backend y frontend para más detalles sobre errores específicos.
