# 📊 Analytics Mejorados - Nube de Palabras

## ✅ Nuevo funcionalidades implementadas

### 1. **Nube de Palabras** (Word Cloud)
Analiza las palabras más frecuentes en las preguntas de los usuarios.

### 2. **Análisis de Temas**
Categoriza palabras por frecuencia: muy frecuente, frecuente, ocasional.

### 3. **Estadísticas de Uso de Documentos**
Muestra qué tan efectivos son los documentos en responder consultas.

---

## 🚀 Nuevos Endpoints API

### 1. Nube de Palabras

**GET** `/analytics/word-cloud`

**Parámetros:**
- `bot_id` (opcional): Filtrar por bot específico
- `days` (default: 30): Días a analizar
- `limit` (default: 50): Número máximo de palabras

**Respuesta:**
```json
{
  "word_cloud": [
    {
      "word": "bootcamp",
      "count": 25,
      "weight": 1.0
    },
    {
      "word": "horas",
      "count": 18,
      "weight": 0.72
    },
    {
      "word": "inscripción",
      "count": 12,
      "weight": 0.48
    }
  ],
  "total_words": 50,
  "period_days": 30,
  "bot_id": "default"
}
```

**Ejemplo de uso:**
```bash
# Todas las palabras (global)
curl http://localhost:8000/analytics/word-cloud?days=30&limit=50

# Por bot específico
curl http://localhost:8000/analytics/word-cloud?bot_id=default&days=7&limit=30
```

---

### 2. Análisis de Temas

**GET** `/analytics/question-topics`

**Parámetros:**
- `bot_id` (opcional): Filtrar por bot específico
- `days` (default: 30): Días a analizar

**Respuesta:**
```json
{
  "topics": {
    "total_unique_words": 87,
    "total_words_analyzed": 450,
    "categories": {
      "muy_frecuente": [
        {
          "word": "bootcamp",
          "count": 45,
          "weight": 1.0,
          "percentage": 10.0
        }
      ],
      "frecuente": [
        {
          "word": "duración",
          "count": 20,
          "weight": 0.44,
          "percentage": 4.4
        }
      ],
      "ocasional": [...]
    }
  },
  "period_days": 30,
  "bot_id": "default"
}
```

**Ejemplo de uso:**
```bash
curl http://localhost:8000/analytics/question-topics?bot_id=default&days=30
```

---

### 3. Uso de Documentos

**GET** `/analytics/document-usage/{bot_id}`

**Parámetros:**
- `bot_id` (requerido): ID del bot
- `days` (default: 30): Días a analizar

**Respuesta:**
```json
{
  "document_usage": {
    "bot_id": "default",
    "period_days": 30,
    "total_queries": 150,
    "avg_sources_per_query": 4.2,
    "queries_with_sources": 145,
    "queries_without_sources": 5
  },
  "period_days": 30
}
```

**Ejemplo de uso:**
```bash
curl http://localhost:8000/analytics/document-usage/default?days=30
```

---

## 🧪 Cómo Probar

### 1. Asegúrate de que el backend esté corriendo

```bash
cd backend
.venv\Scripts\activate
python -m uvicorn app.main:app --reload --port 8000
```

### 2. Haz algunas preguntas al chatbot

Para tener datos en analytics, primero necesitas interacciones. Ve al chat widget y haz preguntas como:

- "¿Cuántas horas dura el bootcamp?"
- "¿Cómo me inscribo al bootcamp?"
- "¿Cuál es el costo del bootcamp?"
- "¿Qué temas cubre el bootcamp?"

### 3. Prueba los nuevos endpoints

**Opción A: Swagger UI (Recomendado)**
- Ve a: http://localhost:8000/docs
- Busca la sección "analytics"
- Prueba cada endpoint directamente desde ahí

**Opción B: cURL**
```bash
# Nube de palabras
curl http://localhost:8000/analytics/word-cloud?bot_id=default&days=30&limit=50

# Temas principales
curl http://localhost:8000/analytics/question-topics?bot_id=default&days=30

# Uso de documentos
curl http://localhost:8000/analytics/document-usage/default?days=30
```

**Opción C: Navegador**
- http://localhost:8000/analytics/word-cloud?bot_id=default&days=30&limit=50
- http://localhost:8000/analytics/question-topics?bot_id=default&days=30
- http://localhost:8000/analytics/document-usage/default?days=30

---

## 📈 Características Técnicas

### Filtrado de Stop Words
El sistema filtra automáticamente palabras comunes en español como:
- Artículos: el, la, los, las, un, una
- Preposiciones: de, en, con, para, por
- Conjunciones: y, o, pero
- Pronombres: yo, tú, él, ella
- Y más de 100 palabras comunes

Solo se analizan palabras de **3 o más caracteres** con significado relevante.

### Normalización de Pesos
Los pesos (weight) están normalizados entre 0 y 1:
- `1.0` = palabra más frecuente
- `0.5` = 50% de frecuencia relativa a la más común
- `0.1` = 10% de frecuencia relativa

Esto facilita la visualización en una nube de palabras donde el tamaño del texto es proporcional al peso.

---

## 🎨 Próximos Pasos: Frontend

Ahora que tenemos los datos, el siguiente paso es crear visualizaciones en el frontend:

1. **Componente de Nube de Palabras**
   - Usar librería como `react-wordcloud` o `d3-cloud`
   - Colores según categoría (muy frecuente, frecuente, ocasional)
   - Interactividad al hacer hover

2. **Gráficos de Tendencias**
   - Evolución temporal de temas
   - Comparativa entre períodos

3. **Dashboard Mejorado**
   - Vista general con word cloud
   - Filtros por bot y período
   - Export a PDF/imagen

---

## 🐛 Troubleshooting

### No aparecen palabras

**Problema**: La nube de palabras está vacía.

**Solución**:
1. Verifica que haya interacciones registradas:
   ```bash
   curl http://localhost:8000/analytics/bot/default?days=30
   ```
2. Haz más preguntas al chatbot para generar datos
3. Verifica que el `bot_id` sea correcto

### Palabras irrelevantes aparecen

**Problema**: Palabras comunes o sin significado aparecen en la nube.

**Solución**: Agrega más palabras al conjunto `STOP_WORDS` en:
```python
backend/app/services/analytics_service.py
```

---

## 📊 Ejemplo de Uso Completo

```bash
# 1. Hacer preguntas al chatbot (genera 10-20 preguntas variadas)

# 2. Ver nube de palabras del último mes
curl http://localhost:8000/analytics/word-cloud?bot_id=default&days=30&limit=50

# 3. Ver análisis de temas
curl http://localhost:8000/analytics/question-topics?bot_id=default&days=30

# 4. Ver estadísticas de uso de documentos
curl http://localhost:8000/analytics/document-usage/default?days=30

# 5. Comparar global vs específico
curl http://localhost:8000/analytics/word-cloud?days=30  # Todos los bots
curl http://localhost:8000/analytics/word-cloud?bot_id=default&days=30  # Solo default
```

---

## ✨ Valor de Negocio

Estas nuevas métricas te permiten:

1. **Entender a tus usuarios**
   - ¿Qué temas les interesan más?
   - ¿Qué palabras usan para buscar información?

2. **Optimizar contenido**
   - Identificar gaps en la documentación
   - Priorizar qué documentos crear/mejorar

3. **Mejorar el chatbot**
   - Ajustar prompts según temas frecuentes
   - Detectar confusiones recurrentes

4. **Reportes ejecutivos**
   - Visualizaciones impactantes para stakeholders
   - Datos concretos sobre uso del sistema

---

**Próximo paso**: Crear el componente visual de nube de palabras en el frontend React.
