# 🎯 Guía de RAG Preciso - Chatbots que Solo Responden con Documentación

## 📋 Descripción

Este sistema garantiza que tus chatbots respondan **ÚNICAMENTE** con información de los documentos que subas, sin inventar ni usar conocimiento general del modelo.

---

## ✨ Características Principales

### **1. Strict Mode (Modo Estricto)**

Cuando está activado, el bot **SOLO** responde con información de los documentos:

```python
strict_mode = True  # ✅ Solo documentos
strict_mode = False  # ⚠️ Puede usar conocimiento general
```

**Comportamiento:**
- ✅ **Si hay docs relevantes** → Responde basándose en ellos
- ❌ **Si NO hay docs relevantes** → Retorna respuesta fallback personalizada
- 🚫 **Nunca inventa información** que no esté en los docs

### **2. Threshold de Similitud (Filtro de Calidad)**

Define qué tan similar debe ser un documento para ser considerado:

```python
retrieval_threshold = 0.3  # 30% de similitud mínima
```

**Escala de similitud (0.0 - 1.0):**
- `1.0` = 100% idéntico
- `0.8` = Muy similar (recomendado para info crítica)
- `0.5` = Moderadamente similar
- `0.3` = Algo relacionado (por defecto)
- `0.1` = Apenas relacionado
- `0.0` = Completamente diferente

**Ejemplo:**
```python
# Usuario pregunta: "¿Cómo reinicio el router?"
# Documento 1: "Para reiniciar el router..." → similarity = 0.95 ✅ INCLUIDO
# Documento 2: "Los routers tienen luces..." → similarity = 0.25 ❌ DESCARTADO
```

### **3. Respuesta Fallback Personalizada**

Mensaje que se muestra cuando no hay información relevante:

```python
fallback_response = "Lo siento, no tengo información sobre eso en mi base de conocimiento."
```

**Puedes personalizarlo:**
```python
# Para soporte técnico:
fallback_response = "No encuentro esa información en nuestros manuales. Contacta a soporte@empresa.com"

# Para e-commerce:
fallback_response = "Ese producto no está en nuestro catálogo actual. ¿Necesitas ayuda con algo más?"

# Para educación:
fallback_response = "Este tema no está cubierto en el material del curso."
```

### **4. Max Sources (Límite de Fuentes)**

Número máximo de fragmentos de documentos a incluir en el contexto:

```python
max_sources = 5  # Máximo 5 fragmentos por respuesta
```

**¿Por qué limitar?**
- ⚡ Respuestas más rápidas
- 💰 Menos tokens = menor costo
- 🎯 Contexto más relevante y enfocado

---

## 🔧 Configuración de un Bot

### **Opción A: Al Crear un Bot (API)**

```json
POST /bots/

{
  "bot_id": "soporte-tecnico",
  "name": "Asistente de Soporte",
  "system_prompt": "Eres un asistente de soporte técnico profesional...",
  "temperature": 0.7,

  // ✨ Configuración RAG Preciso
  "strict_mode": true,
  "retrieval_threshold": 0.4,
  "fallback_response": "No encuentro esa información. Contacta a soporte@empresa.com",
  "max_sources": 5,
  "retrieval_k": 10  // Cuántos docs buscar antes de filtrar
}
```

### **Opción B: Actualizar Bot Existente**

```json
PATCH /bots/soporte-tecnico

{
  "strict_mode": true,
  "retrieval_threshold": 0.5,
  "fallback_response": "Información no disponible en documentación."
}
```

### **Opción C: Usando Presets Optimizados**

```json
POST /bots/

{
  "bot_id": "mi-bot",
  "name": "Mi Bot",
  "system_prompt": "rag_strict",  // ✅ Usa preset ultra-estricto
  "strict_mode": true,
  "retrieval_threshold": 0.4
}
```

**Presets disponibles:**
1. **`rag_strict`** - Máxima precisión, solo documentos
2. **`rag_flexible`** - Permite complementar con conocimiento general
3. **`support`** - Optimizado para soporte técnico
4. **`educational`** - Optimizado para educación
5. **`sales`** - Optimizado para ventas
6. **`legal`** - Optimizado para investigación legal

---

## 📊 Ejemplos de Uso

### **Ejemplo 1: Soporte Técnico Ultra-Preciso**

```json
{
  "bot_id": "soporte-premium",
  "name": "Soporte Premium",
  "system_prompt": "rag_strict",
  "strict_mode": true,
  "retrieval_threshold": 0.6,  // Solo info muy relevante
  "fallback_response": "Esta información no está en nuestros manuales oficiales. Por favor contacta a soporte técnico al 555-1234.",
  "max_sources": 3,  // Solo las 3 mejores fuentes
  "retrieval_k": 15  // Buscar en 15 docs, pero solo usar los mejores
}
```

**Resultado:**
- ✅ Solo responde si tiene info muy relevante (60%+ similitud)
- ✅ Limita respuesta a las 3 mejores fuentes
- ✅ Si no encuentra nada, da número de contacto

### **Ejemplo 2: E-commerce Preciso**

```json
{
  "bot_id": "tienda-bot",
  "name": "Asistente de Ventas",
  "system_prompt": "sales",
  "strict_mode": true,
  "retrieval_threshold": 0.3,  // Más flexible para productos similares
  "fallback_response": "Ese producto no está disponible. ¿Te gustaría ver productos similares?",
  "max_sources": 5
}
```

**Resultado:**
- ✅ Solo recomienda productos del catálogo
- ✅ Nunca inventa precios o promociones
- ✅ Sugiere alternativas cuando no hay match exacto

### **Ejemplo 3: Educación Estricta**

```json
{
  "bot_id": "tutor-matematicas",
  "name": "Tutor de Matemáticas",
  "system_prompt": "educational",
  "strict_mode": true,
  "retrieval_threshold": 0.5,
  "fallback_response": "Este tema no está en el material del curso. Consulta con el profesor.",
  "max_sources": 4
}
```

**Resultado:**
- ✅ Solo explica conceptos del material del curso
- ✅ No da soluciones de temas no cubiertos
- ✅ Guía al estudiante al profesor si es necesario

---

## 🧪 Testing del Sistema

### **Test 1: Pregunta con Documentación Relevante**

```python
# Documentos subidos:
# - manual.pdf: "Para reiniciar el router, desconecta el cable por 30 segundos."

# Pregunta del usuario:
"¿Cómo reinicio mi router?"

# Respuesta esperada:
"Para reiniciar el router, desconecta el cable de alimentación por 30 segundos y vuelve a conectarlo."

# ✅ Respuesta basada en el manual
```

### **Test 2: Pregunta SIN Documentación Relevante**

```python
# Documentos subidos:
# - manual.pdf (sobre routers)

# Pregunta del usuario:
"¿Cuál es la capital de Francia?"

# Respuesta esperada (strict_mode=True):
"Lo siento, no tengo información sobre eso en mi base de conocimiento."

# ✅ Fallback response activado
```

### **Test 3: Threshold Filtering**

```python
# Configuración:
retrieval_threshold = 0.5  # 50% mínimo

# Pregunta:
"¿Cómo configuro WiFi?"

# Documentos encontrados:
# Doc 1: "Configuración WiFi paso a paso..." → 0.85 ✅ INCLUIDO
# Doc 2: "El WiFi usa ondas de radio..." → 0.35 ❌ DESCARTADO

# Respuesta:
# Solo usa Doc 1 (0.85 > 0.5)
```

---

## 🎯 Recomendaciones por Caso de Uso

### **Soporte Técnico Crítico**

```json
{
  "strict_mode": true,
  "retrieval_threshold": 0.6,
  "max_sources": 3,
  "fallback_response": "Contacta a soporte urgente"
}
```

**Por qué:**
- Info incorrecta puede causar daños
- Mejor derivar a humano que dar info dudosa

### **E-commerce / Ventas**

```json
{
  "strict_mode": true,
  "retrieval_threshold": 0.3,
  "max_sources": 5,
  "fallback_response": "Producto no disponible"
}
```

**Por qué:**
- Necesita flexibilidad para productos similares
- Más fuentes = mejores recomendaciones

### **Educación / Tutorías**

```json
{
  "strict_mode": true,
  "retrieval_threshold": 0.5,
  "max_sources": 4,
  "fallback_response": "Tema no cubierto en el curso"
}
```

**Por qué:**
- Balance entre precisión y cobertura
- Guía al estudiante correctamente

### **Legal / Compliance**

```json
{
  "strict_mode": true,
  "retrieval_threshold": 0.7,
  "max_sources": 2,
  "fallback_response": "Consulta con un abogado profesional"
}
```

**Por qué:**
- Máxima precisión requerida
- Info errónea tiene consecuencias legales

---

## 📈 Mejores Prácticas

### **1. Sube Documentación de Calidad**

✅ **Bueno:**
```
Archivo: manual-router-modelo-X.pdf
Contenido: "Para reiniciar el router modelo X:
1. Desconecta el cable de alimentación
2. Espera 30 segundos
3. Vuelve a conectar"
```

❌ **Malo:**
```
Archivo: notas_varias.txt
Contenido: "router, reinicio, nose, preguntar a Juan"
```

### **2. Estructura tus Documentos**

✅ **Bueno:**
```markdown
# Título claro
## Subtítulo específico

Contenido bien organizado con:
- Listas numeradas para pasos
- Ejemplos concretos
- Casos de uso
```

❌ **Malo:**
```
texto todo junto sin formato ni estructura
```

### **3. Ajusta el Threshold Gradualmente**

```python
# Empieza conservador
retrieval_threshold = 0.5

# Prueba con usuarios reales
# Si muchas preguntas no se responden → baja a 0.3
# Si hay respuestas irrelevantes → sube a 0.6

# Encuentra el balance óptimo
retrieval_threshold = 0.4  # Sweet spot para tu caso
```

### **4. Monitorea las Métricas**

```python
GET /analytics/bot/mi-bot?days=7

{
  "total_interactions": 150,
  "fallback_responses": 45,  // 30% fueron fallback
  "avg_similarity": 0.52,    // Similitud promedio
  "sources_per_response": 3.2
}

# Si fallback_responses es muy alto (>50%) → baja el threshold
# Si avg_similarity es bajo (<0.4) → mejora los documentos
```

---

## 🚨 Troubleshooting

### **Problema 1: "El bot nunca responde, siempre fallback"**

**Causa:** Threshold muy alto o documentos no relevantes

**Solución:**
```json
// Baja el threshold temporalmente
{
  "retrieval_threshold": 0.2  // Era 0.6
}

// Y revisa los documentos subidos
GET /documents/list?bot_id=mi-bot
```

### **Problema 2: "El bot da respuestas irrelevantes"**

**Causa:** Threshold muy bajo

**Solución:**
```json
// Sube el threshold
{
  "retrieval_threshold": 0.5  // Era 0.2
}

// Y activa strict_mode
{
  "strict_mode": true
}
```

### **Problema 3: "Respuestas muy largas o confusas"**

**Causa:** Demasiadas fuentes

**Solución:**
```json
{
  "max_sources": 2  // Era 10
}
```

---

## 📊 Comparación: Antes vs Ahora

| Aspecto | Antes (Sin RAG Preciso) | Ahora (Con RAG Preciso) |
|---------|-------------------------|-------------------------|
| **Precisión** | ⚠️ A veces inventa info | ✅ Solo info verificada |
| **Confiabilidad** | ❌ Inconsistente | ✅ 100% confiable |
| **Control** | ❌ Poco control | ✅ Control total |
| **Fallback** | ❌ Responde cualquier cosa | ✅ Fallback personalizado |
| **Filtrado** | ❌ No filtra | ✅ Threshold configurable |
| **Fuentes** | ❌ Sin límite | ✅ Max sources definido |

---

## ✅ Checklist de Configuración

Usa este checklist al crear un nuevo bot:

- [ ] Definir caso de uso (soporte, ventas, educación, etc.)
- [ ] Elegir preset de prompt apropiado
- [ ] Configurar `strict_mode = true` (recomendado)
- [ ] Ajustar `retrieval_threshold` según criticidad:
  - [ ] 0.7+ para legal/crítico
  - [ ] 0.5 para educación
  - [ ] 0.3 para ventas/general
- [ ] Personalizar `fallback_response` con acción clara
- [ ] Definir `max_sources` (3-5 recomendado)
- [ ] Subir documentación de calidad
- [ ] Probar con preguntas reales
- [ ] Monitorear métricas
- [ ] Ajustar configuración según resultados

---

**Con esta configuración, tus chatbots serán ultra-precisos y solo responderán con la información que tú les proporciones. ¡Cero alucinaciones garantizadas!** 🎯
