# Plan de Desarrollo Frontend - Chatbot RAG Multi-Tenant

## 🎨 Visión General

Desarrollo de un frontend completo en React con dos componentes principales:
1. **Admin Dashboard**: Panel de administración para gestionar bots, documentos y ver analytics
2. **Embeddable Chat Widget**: Widget de chat que se puede integrar en cualquier sitio web

---

## 🏗️ Arquitectura del Frontend

```
frontend/
├── admin-dashboard/           # Aplicación principal de administración
│   ├── src/
│   │   ├── components/        # Componentes reutilizables
│   │   ├── pages/            # Páginas principales
│   │   ├── services/         # API clients
│   │   ├── hooks/            # Custom hooks
│   │   ├── context/          # Context API
│   │   ├── utils/            # Utilidades
│   │   └── App.tsx           # Root component
│   └── package.json
│
└── chat-widget/              # Widget embebible
    ├── src/
    │   ├── components/       # Componentes del chat
    │   ├── services/        # API client
    │   ├── types/           # TypeScript types
    │   └── index.tsx        # Entry point
    ├── dist/                # Build para distribución
    └── package.json
```

---

## 📱 1. Admin Dashboard

### Stack Tecnológico

- **Framework**: React 18 + TypeScript
- **Build**: Vite
- **Routing**: React Router v6
- **State**: React Query (TanStack Query) + Zustand
- **UI**: Tailwind CSS + shadcn/ui
- **Forms**: React Hook Form + Zod
- **Charts**: Recharts
- **HTTP**: Axios
- **Icons**: Lucide React

### Páginas Principales

#### 1.1 Dashboard Home (`/`)
```tsx
// Vista general con métricas clave
- Total de bots activos
- Interacciones hoy
- Documentos indexados
- Gráfico de interacciones (últimos 7 días)
- Top 5 bots más usados
- Alertas/notificaciones
```

#### 1.2 Gestión de Bots (`/bots`)
```tsx
// Lista de bots con acciones
- Tabla/Grid de bots
  - Nombre, ID, status (activo/inactivo)
  - Última actualización
  - # de documentos
  - # de interacciones
  - Acciones: Editar, Eliminar, Ver stats

// Botón: Crear nuevo bot
- Modal/Drawer con formulario:
  - Bot ID (único)
  - Nombre
  - Descripción
  - System Prompt (editor de texto o selector de presets)
  - Temperature (slider 0-2)
  - Retrieval K (número de chunks)
  - Metadata personalizada (JSON editor)
```

#### 1.3 Detalles de Bot (`/bots/:botId`)
```tsx
// Página completa de un bot
Secciones:
1. Información General
   - Editar inline
   - Activar/Desactivar
   - Cambiar prompt

2. Documentos
   - Drag & drop para subir
   - Lista de documentos actuales
   - Preview/Download
   - Eliminar

3. Analytics
   - Métricas del bot (últimos 7/30 días)
   - Gráfico de interacciones
   - Tiempo de respuesta promedio
   - Tasa de éxito
   - Preguntas populares

4. Prueba en Vivo
   - Chat integrado para probar el bot
   - Ver sources y debug info
```

#### 1.4 Documentos Globales (`/documents`)
```tsx
// Vista global de todos los documentos
- Tabla con filtros:
  - Nombre archivo
  - Bot asociado
  - Fecha de subida
  - # de chunks
  - Tipo de archivo
  - Acciones: Ver, Descargar, Eliminar

// Filtros y búsqueda:
- Por bot
- Por fecha
- Por tipo de archivo
- Búsqueda por nombre
```

#### 1.5 Analytics Global (`/analytics`)
```tsx
// Dashboard de analytics general
Widgets:
1. Métricas Overview
   - Total interacciones (filtrable por período)
   - Bots activos
   - Success rate global
   - Tiempo respuesta promedio

2. Gráficos
   - Interacciones por día (line chart)
   - Distribución por bot (pie chart)
   - Tiempos de respuesta (bar chart)
   - Tendencias de uso (area chart)

3. Tablas
   - Preguntas más frecuentes (global)
   - Bots más usados
   - Documentos más consultados
   - Errores recientes

4. Exportación
   - Descargar CSV/JSON
   - Filtros de fecha
   - Selección de métricas
```

#### 1.6 Configuración (`/settings`)
```tsx
// Configuración del sistema
Secciones:
1. Configuración LLM
   - Proveedor actual (Ollama/OpenAI)
   - Modelo seleccionado
   - API keys (ofuscadas)
   - Test de conexión

2. Configuración General
   - Nombre de la aplicación
   - URL del backend
   - Límites (max docs, max bots)
   - Retención de datos analytics

3. Mantenimiento
   - Limpiar analytics antiguos
   - Respaldar configuración
   - Ver logs

4. Embeds
   - Generador de código del widget
   - Preview del widget
```

#### 1.7 Widget Generator (`/embed`)
```tsx
// Generador de código para embeber el widget
Interface:
1. Selector de bot
2. Configuración visual:
   - Color primario
   - Posición (bottom-right, bottom-left, etc)
   - Tamaño inicial
   - Avatar/icono
   - Mensaje de bienvenida

3. Preview en tiempo real

4. Código generado:
   <script src="https://your-domain.com/widget.js"></script>
   <script>
     ChatbotWidget.init({
       botId: 'your-bot-id',
       apiUrl: 'https://api.your-domain.com',
       primaryColor: '#3B82F6',
       position: 'bottom-right'
     });
   </script>

5. Instrucciones de instalación
```

### Componentes Reutilizables

```tsx
// components/ui/ (usando shadcn/ui)
- Button
- Input
- Select
- Dialog/Modal
- Drawer
- Table
- Card
- Badge
- Alert
- Tabs
- Dropdown
- Toast/Notification
- Skeleton (loading)
- Progress Bar
- Slider
- Switch
- Textarea
- DatePicker

// components/custom/
- BotCard
- DocumentUploader
- StatCard
- MetricChart
- PromptEditor
- JsonEditor
- CodeBlock
- SearchBar
- EmptyState
- ErrorBoundary
```

### Services (API Client)

```typescript
// services/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 30000
});

// services/bots.service.ts
export const botsService = {
  list: () => api.get('/bots'),
  get: (botId: string) => api.get(`/bots/${botId}`),
  create: (data: BotCreate) => api.post('/bots', data),
  update: (botId: string, data: BotUpdate) => api.put(`/bots/${botId}`, data),
  delete: (botId: string) => api.delete(`/bots/${botId}`),
  getPresets: () => api.get('/bots/presets/prompts')
};

// services/documents.service.ts
export const documentsService = {
  upload: (file: File, botId: string) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post(`/documents/upload?bot_id=${botId}`, formData);
  },
  list: (botId?: string) => api.get('/documents/list', { params: { bot_id: botId } }),
  delete: (docId: string) => api.delete(`/documents/${docId}`)
};

// services/chat.service.ts
export const chatService = {
  sendMessage: (question: string, botId: string) =>
    api.post('/chat', { question, bot_id: botId })
};

// services/analytics.service.ts
export const analyticsService = {
  getBotStats: (botId: string, days: number) =>
    api.get(`/analytics/bot/${botId}`, { params: { days } }),
  getGlobalStats: (days: number) =>
    api.get('/analytics/global', { params: { days } }),
  getPopularQuestions: (botId?: string, limit = 10) =>
    api.get('/analytics/popular-questions', { params: { bot_id: botId, limit } })
};
```

### Hooks Personalizados

```typescript
// hooks/useBots.ts
export const useBots = () => {
  return useQuery({
    queryKey: ['bots'],
    queryFn: botsService.list
  });
};

// hooks/useBot.ts
export const useBot = (botId: string) => {
  return useQuery({
    queryKey: ['bot', botId],
    queryFn: () => botsService.get(botId)
  });
};

// hooks/useCreateBot.ts
export const useCreateBot = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: botsService.create,
    onSuccess: () => {
      queryClient.invalidateQueries(['bots']);
      toast.success('Bot creado exitosamente');
    }
  });
};

// hooks/useDocuments.ts
export const useDocuments = (botId?: string) => {
  return useQuery({
    queryKey: ['documents', botId],
    queryFn: () => documentsService.list(botId)
  });
};

// hooks/useAnalytics.ts
export const useAnalytics = (botId?: string, days = 7) => {
  return useQuery({
    queryKey: ['analytics', botId, days],
    queryFn: () =>
      botId
        ? analyticsService.getBotStats(botId, days)
        : analyticsService.getGlobalStats(days)
  });
};
```

### State Management

```typescript
// store/useAuthStore.ts (Zustand)
interface AuthState {
  user: User | null;
  token: string | null;
  login: (credentials: Credentials) => Promise<void>;
  logout: () => void;
}

// store/useUIStore.ts
interface UIState {
  sidebarOpen: boolean;
  theme: 'light' | 'dark';
  toggleSidebar: () => void;
  setTheme: (theme: 'light' | 'dark') => void;
}
```

---

## 💬 2. Embeddable Chat Widget

### Características del Widget

```tsx
// Widget totalmente auto-contenido
- Single file JavaScript (widget.js)
- CSS inline (no conflictos con sitio host)
- Shadow DOM para aislamiento
- Responsive
- Accesible (ARIA)
- i18n (español/inglés)
```

### Estructura del Widget

```typescript
// ChatWidget.tsx
interface ChatWidgetProps {
  botId: string;
  apiUrl: string;
  primaryColor?: string;
  position?: 'bottom-right' | 'bottom-left';
  greeting?: string;
  avatar?: string;
  placeholder?: string;
  height?: string;
  width?: string;
}

// Componentes internos:
- ChatBubble (botón flotante)
- ChatWindow (ventana de chat)
- MessageList
- MessageInput
- TypingIndicator
- SourcesList
```

### Estados del Widget

```tsx
1. Minimizado (Bubble)
   - Icono flotante
   - Badge con contador (opcional)
   - Animación de "nuevo mensaje"

2. Expandido (Window)
   - Header:
     - Nombre del bot
     - Status (online/offline)
     - Minimizar, Cerrar
   - Body:
     - Lista de mensajes
     - Scroll automático
     - Loading states
   - Footer:
     - Input de texto
     - Botón enviar
     - "Powered by YourBrand"
```

### API del Widget

```javascript
// Inicialización
ChatbotWidget.init({
  botId: 'my-bot',
  apiUrl: 'https://api.example.com',
  primaryColor: '#3B82F6',
  position: 'bottom-right',
  greeting: '¡Hola! ¿En qué puedo ayudarte?',
  placeholder: 'Escribe tu pregunta...',
  locale: 'es'
});

// Métodos públicos
ChatbotWidget.open();          // Abrir widget
ChatbotWidget.close();         // Cerrar widget
ChatbotWidget.toggle();        // Toggle estado
ChatbotWidget.sendMessage(text); // Enviar mensaje programáticamente
ChatbotWidget.destroy();       // Eliminar widget

// Eventos
ChatbotWidget.on('message', (data) => {
  console.log('New message:', data);
});

ChatbotWidget.on('open', () => {
  console.log('Widget opened');
});

ChatbotWidget.on('close', () => {
  console.log('Widget closed');
});
```

### Build del Widget

```javascript
// vite.config.ts
export default defineConfig({
  build: {
    lib: {
      entry: 'src/index.tsx',
      name: 'ChatbotWidget',
      fileName: 'widget',
      formats: ['iife']  // Single file para <script>
    },
    rollupOptions: {
      output: {
        inlineDynamicImports: true,
        assetFileNames: 'widget.[ext]'
      }
    }
  }
});

// Output: widget.js (todo incluido)
```

---

## 🎨 Diseño Visual

### Paleta de Colores

```css
/* Admin Dashboard */
--primary: #3B82F6;      /* Blue */
--secondary: #8B5CF6;    /* Purple */
--success: #10B981;      /* Green */
--warning: #F59E0B;      /* Orange */
--danger: #EF4444;       /* Red */
--gray-50: #F9FAFB;
--gray-900: #111827;

/* Widget (customizable) */
--widget-primary: var(--primary);
--widget-bg: white;
--widget-text: #111827;
```

### Responsive Breakpoints

```css
/* Tailwind defaults */
sm: 640px   /* Mobile landscape */
md: 768px   /* Tablet */
lg: 1024px  /* Desktop */
xl: 1280px  /* Large desktop */
2xl: 1536px /* Extra large */
```

---

## 🚀 Plan de Implementación

### Fase 1: Setup (1-2 días)

- [ ] Crear proyectos con Vite
- [ ] Configurar TypeScript
- [ ] Setup Tailwind + shadcn/ui
- [ ] Configurar React Router
- [ ] Setup React Query
- [ ] Crear servicios API base

### Fase 2: Admin Dashboard Core (3-4 días)

- [ ] Layout principal (sidebar + topbar)
- [ ] Dashboard home (métricas overview)
- [ ] Página de listado de bots
- [ ] Crear/editar bot (formularios)
- [ ] Navegación y routing

### Fase 3: Gestión de Documentos (2-3 días)

- [ ] Componente de upload (drag & drop)
- [ ] Lista de documentos por bot
- [ ] Integración con API de documentos
- [ ] Estados de loading/error
- [ ] Eliminar documentos

### Fase 4: Analytics Dashboard (2-3 días)

- [ ] Gráficos con Recharts
- [ ] Métricas por bot
- [ ] Analytics globales
- [ ] Filtros de fecha
- [ ] Exportación de datos

### Fase 5: Chat Widget Base (3-4 días)

- [ ] Estructura básica del widget
- [ ] Chat UI (bubble + window)
- [ ] Integración con API de chat
- [ ] Estados (loading, typing, error)
- [ ] Responsive design

### Fase 6: Widget Avanzado (2-3 días)

- [ ] Customización visual
- [ ] Shadow DOM
- [ ] Build optimizado
- [ ] API pública del widget
- [ ] Documentación de uso

### Fase 7: Generador de Embeds (1-2 días)

- [ ] Página de configuración visual
- [ ] Preview en tiempo real
- [ ] Generador de código
- [ ] Copiar al portapapeles
- [ ] Instrucciones de instalación

### Fase 8: Polish y Testing (2-3 días)

- [ ] Optimización de rendimiento
- [ ] Manejo de errores
- [ ] Loading states
- [ ] Accesibilidad (a11y)
- [ ] Testing de componentes clave
- [ ] Documentación

**Total estimado: 16-24 días** (2-3 semanas)

---

## 🌟 Features Extra (Nice to Have)

### Admin Dashboard
- [ ] Dark mode
- [ ] Multi-idioma (i18n)
- [ ] Notificaciones en tiempo real
- [ ] Exportar/Importar configuración de bots
- [ ] Plantillas de bots
- [ ] Búsqueda global
- [ ] Atajos de teclado
- [ ] Tour guiado (onboarding)

### Chat Widget
- [ ] Modo oscuro
- [ ] Emojis
- [ ] Markdown en respuestas
- [ ] Historial de conversaciones
- [ ] Feedback (👍👎)
- [ ] Sugerencias de preguntas
- [ ] Voice input
- [ ] Modo fullscreen
- [ ] Temas predefinidos

---

## 📦 Dependencias Principales

### Admin Dashboard
```json
{
  "dependencies": {
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "react-router-dom": "^6.20.0",
    "@tanstack/react-query": "^5.17.0",
    "zustand": "^4.4.7",
    "axios": "^1.6.2",
    "react-hook-form": "^7.49.0",
    "zod": "^3.22.4",
    "@hookform/resolvers": "^3.3.2",
    "recharts": "^2.10.0",
    "lucide-react": "^0.300.0",
    "date-fns": "^3.0.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.45",
    "@vitejs/plugin-react": "^4.2.1",
    "vite": "^5.0.8",
    "typescript": "^5.3.3",
    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32"
  }
}
```

### Chat Widget
```json
{
  "dependencies": {
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "axios": "^1.6.2"
  },
  "devDependencies": {
    "@types/react": "^18.2.45",
    "@vitejs/plugin-react": "^4.2.1",
    "vite": "^5.0.8",
    "typescript": "^5.3.3"
  }
}
```

---

## 🎯 Resultados Esperados

Al finalizar el desarrollo, tendrás:

1. **Admin Dashboard profesional** para gestionar todo el sistema
2. **Chat Widget embebible** listo para usar en cualquier sitio
3. **Generador de código** para facilitar la integración
4. **Sistema completo de analytics** para tomar decisiones
5. **UI moderna y responsive** con Tailwind + shadcn/ui
6. **TypeScript** para type safety
7. **Documentación completa** de uso

---

## 🚀 Siguiente Paso

¿Quieres que comience con el desarrollo del frontend? Puedo empezar por:

1. **Setup inicial** de ambos proyectos
2. **Admin Dashboard** layout y primeras páginas
3. **Chat Widget** básico funcional
4. O cualquier otra parte que prefieras priorizar

¡Dime por dónde empezamos y le daremos forma a este sistema de chatbots RAG profesional!
