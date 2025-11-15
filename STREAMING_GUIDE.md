# ⚡ Guía de Streaming de Respuestas (Server-Sent Events)

## 📋 Descripción

Sistema de streaming de respuestas en tiempo real usando **Server-Sent Events (SSE)**.

Las respuestas se envían **palabra por palabra** mientras el modelo las genera, creando una experiencia similar a ChatGPT.

---

## ✨ Ventajas del Streaming

| Sin Streaming | Con Streaming ⚡ |
|---------------|------------------|
| ⏰ Usuario espera 5-10 segundos | ✅ Usuario ve progreso inmediato |
| 😴 Pantalla estática mientras carga | ✅ Efecto de escritura en tiempo real |
| ❌ No sabe si está procesando o colgado | ✅ Feedback visual constante |
| 🐌 Experiencia lenta y frustrante | ✅ Experiencia fluida y moderna |

**Resultado**: Mejora drástica en la UX percibida, incluso si el tiempo total es el mismo.

---

## 🚀 Quick Start

### **Backend (Ya Implementado)**

```python
# Endpoint: POST /chat/stream
```

### **Frontend (React/TypeScript)**

```typescript
async function streamChatResponse(question: string, botId: string) {
  const response = await fetch('http://localhost:8000/chat/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ question, bot_id: botId }),
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split('\n');

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = JSON.parse(line.slice(6));

        if (data.type === 'metadata') {
          console.log('Fuentes:', data.sources);
        } else if (data.type === 'chunk') {
          console.log('Texto:', data.content);
          // Agregar al DOM
        } else if (data.type === 'done') {
          console.log('Respuesta completa');
        }
      }
    }
  }
}
```

---

## 📡 Formato de Respuesta (SSE)

### **1. Metadata Inicial**

```json
data: {
  "type": "metadata",
  "sources": [
    {
      "text": "Fragmento del documento...",
      "similarity": 0.85,
      "metadata": {"filename": "manual.pdf"}
    }
  ],
  "bot_config": {
    "bot_id": "soporte-tech",
    "name": "Asistente de Soporte",
    "strict_mode": true,
    "threshold": 0.4,
    "sources_found": 3
  }
}
```

### **2. Chunks de Texto**

```json
data: {"type": "chunk", "content": "Para"}

data: {"type": "chunk", "content": " reiniciar"}

data: {"type": "chunk", "content": " el"}

data: {"type": "chunk", "content": " router"}
```

### **3. Señal de Finalización**

```json
data: {"type": "done"}
```

### **4. Fallback (Strict Mode sin Docs)**

```json
data: {"type": "metadata", "sources": [], "bot_config": {...}}

data: {"type": "chunk", "content": "Lo siento, no tengo información..."}

data: {"type": "done", "fallback": true}
```

### **5. Error**

```json
data: {"type": "error", "message": "Bot no está disponible"}
```

---

## 💻 Ejemplos de Integración

### **React Hook Personalizado**

```typescript
// hooks/useStreamChat.ts
import { useState, useCallback } from 'react';

interface StreamMessage {
  text: string;
  sources: any[];
  isComplete: boolean;
  isFallback: boolean;
}

export function useStreamChat() {
  const [message, setMessage] = useState<StreamMessage>({
    text: '',
    sources: [],
    isComplete: false,
    isFallback: false,
  });
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const streamChat = useCallback(async (question: string, botId: string) => {
    setIsStreaming(true);
    setError(null);
    setMessage({ text: '', sources: [], isComplete: false, isFallback: false });

    try {
      const response = await fetch('http://localhost:8000/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, bot_id: botId }),
      });

      if (!response.ok) {
        throw new Error('Error en la respuesta');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();

        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));

              if (data.type === 'metadata') {
                setMessage(prev => ({ ...prev, sources: data.sources }));
              } else if (data.type === 'chunk') {
                setMessage(prev => ({ ...prev, text: prev.text + data.content }));
              } else if (data.type === 'done') {
                setMessage(prev => ({
                  ...prev,
                  isComplete: true,
                  isFallback: data.fallback || false,
                }));
              } else if (data.type === 'error') {
                setError(data.message);
              }
            } catch (e) {
              console.error('Error parsing SSE:', e);
            }
          }
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
    } finally {
      setIsStreaming(false);
    }
  }, []);

  return { message, isStreaming, error, streamChat };
}
```

### **Componente de Chat con Streaming**

```tsx
// components/StreamingChat.tsx
import React, { useState } from 'react';
import { useStreamChat } from '../hooks/useStreamChat';

export function StreamingChat({ botId }: { botId: string }) {
  const [question, setQuestion] = useState('');
  const { message, isStreaming, error, streamChat } = useStreamChat();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    await streamChat(question, botId);
  };

  return (
    <div className="chat-container">
      {/* Mensaje del bot con efecto de typing */}
      {message.text && (
        <div className="bot-message">
          <div className="message-content">
            {message.text}
            {/* Cursor parpadeante mientras escribe */}
            {isStreaming && <span className="typing-cursor">|</span>}
          </div>

          {/* Fuentes usadas */}
          {message.sources.length > 0 && (
            <div className="sources">
              <h4>Fuentes:</h4>
              {message.sources.map((source, i) => (
                <div key={i} className="source">
                  <span>Similitud: {(source.similarity * 100).toFixed(1)}%</span>
                  <p>{source.text.slice(0, 100)}...</p>
                </div>
              ))}
            </div>
          )}

          {/* Badge si es fallback */}
          {message.isFallback && (
            <span className="fallback-badge">
              ℹ️ Sin información en documentos
            </span>
          )}
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="error-message">
          ❌ {error}
        </div>
      )}

      {/* Input */}
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Escribe tu pregunta..."
          disabled={isStreaming}
        />
        <button type="submit" disabled={isStreaming}>
          {isStreaming ? 'Procesando...' : 'Enviar'}
        </button>
      </form>
    </div>
  );
}
```

### **CSS para Efecto de Typing**

```css
/* Cursor parpadeante */
.typing-cursor {
  display: inline-block;
  animation: blink 1s infinite;
  margin-left: 2px;
}

@keyframes blink {
  0%, 49% { opacity: 1; }
  50%, 100% { opacity: 0; }
}

/* Animación de aparición suave */
.bot-message {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Fuentes colapsables */
.sources {
  margin-top: 12px;
  padding: 12px;
  background: #f5f5f5;
  border-radius: 8px;
}

.source {
  padding: 8px;
  border-left: 3px solid #007bff;
  margin-top: 8px;
  background: white;
}

/* Badge de fallback */
.fallback-badge {
  display: inline-block;
  margin-top: 8px;
  padding: 4px 8px;
  background: #ffc107;
  color: #000;
  border-radius: 4px;
  font-size: 0.9em;
}
```

---

## 🧪 Testing del Streaming

### **Test 1: cURL**

```bash
curl -N -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"question": "¿Cómo reinicio el router?", "bot_id": "soporte-tech"}'

# -N = --no-buffer (ver chunks en tiempo real)
```

**Salida esperada:**
```
data: {"type":"metadata","sources":[...],"bot_config":{...}}

data: {"type":"chunk","content":"Para"}

data: {"type":"chunk","content":" reiniciar"}

data: {"type":"chunk","content":" el"}

data: {"type":"chunk","content":" router"}

...

data: {"type":"done"}
```

### **Test 2: JavaScript Fetch**

```javascript
async function testStreaming() {
  const response = await fetch('http://localhost:8000/chat/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question: '¿Cómo reinicio el router?',
      bot_id: 'soporte-tech'
    })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    console.log(decoder.decode(value));
  }
}

testStreaming();
```

### **Test 3: EventSource (Alternativa)**

⚠️ **Nota**: EventSource solo soporta GET. Para POST, usa Fetch API.

```javascript
// NO FUNCIONA con POST:
const eventSource = new EventSource('/chat/stream');

// Usar Fetch API en su lugar (como se muestra arriba)
```

---

## 🔧 Configuración Avanzada

### **Timeout**

```typescript
// Timeout de 60 segundos
const controller = new AbortController();
const timeoutId = setTimeout(() => controller.abort(), 60000);

const response = await fetch('http://localhost:8000/chat/stream', {
  method: 'POST',
  signal: controller.signal,
  // ...
});

clearTimeout(timeoutId);
```

### **Retry en Errores**

```typescript
async function streamWithRetry(question: string, botId: string, maxRetries = 3) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      await streamChat(question, botId);
      return; // Éxito
    } catch (error) {
      if (attempt === maxRetries) throw error;

      console.log(`Reintento ${attempt}/${maxRetries}...`);
      await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
    }
  }
}
```

### **Cancelación**

```typescript
const controller = new AbortController();

// En el fetch:
fetch(url, { signal: controller.signal, ... });

// Para cancelar:
controller.abort();
```

---

## 📊 Métricas y Analytics

```typescript
// Trackear tiempo de primer chunk
const startTime = Date.now();
let firstChunkTime: number | null = null;

// En el handler del primer chunk:
if (data.type === 'chunk' && firstChunkTime === null) {
  firstChunkTime = Date.now() - startTime;
  console.log('Time to first chunk:', firstChunkTime, 'ms');
}

// Trackear tiempo total
if (data.type === 'done') {
  const totalTime = Date.now() - startTime;
  console.log('Total time:', totalTime, 'ms');

  // Enviar a analytics
  analytics.track('chat_streaming_completed', {
    bot_id: botId,
    time_to_first_chunk: firstChunkTime,
    total_time: totalTime,
    chunks_received: chunkCount,
    sources_used: sources.length,
  });
}
```

---

## 🚨 Troubleshooting

### **Problema 1: "No veo chunks, solo la respuesta completa"**

**Causa**: Buffering en nginx o proxy

**Solución**:
```nginx
# En nginx.conf
proxy_buffering off;
proxy_cache off;
```

**O en FastAPI** (ya incluido):
```python
headers={"X-Accel-Buffering": "no"}
```

### **Problema 2: "Connection timeout"**

**Causa**: Timeout del servidor

**Solución**:
```python
# En uvicorn
uvicorn app.main:app --timeout-keep-alive 120
```

### **Problema 3: "CORS error"**

**Causa**: Falta configuración CORS

**Solución**:
```python
# En FastAPI
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción: ["https://tu-dominio.com"]
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## ✅ Checklist de Implementación

- [ ] Backend streaming configurado ✅ (Ya está)
- [ ] Hook useStreamChat creado
- [ ] Componente StreamingChat implementado
- [ ] CSS de typing cursor agregado
- [ ] Manejo de errores implementado
- [ ] Timeout configurado
- [ ] Cancelación de requests implementada
- [ ] Métricas de performance agregadas
- [ ] Testing en navegador realizado
- [ ] Testing en móviles realizado

---

**¡Streaming de respuestas listo! Experiencia de chat moderna y fluida garantizada.** ⚡
