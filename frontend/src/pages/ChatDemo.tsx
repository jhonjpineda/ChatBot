import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { botsService } from '../services/bots.service';
import ChatWidget from '../components/ChatWidget';

export default function ChatDemo() {
  const [selectedBotId, setSelectedBotId] = useState<string>('default');
  const [showWidget, setShowWidget] = useState(false);

  // Fetch bots for selector
  const { data: botsData } = useQuery({
    queryKey: ['bots'],
    queryFn: () => botsService.list(true),
  });

  const bots = botsData?.bots || [];

  // Get selected bot details
  const selectedBot = bots.find((bot) => bot.bot_id === selectedBotId);

  const embedCode = `<!-- Chatbot Widget -->
<div id="chatbot-widget-root"></div>
<script src="https://tu-cdn.com/widget.iife.js"></script>
<script>
  ChatbotWidget.init({
    botId: '${selectedBotId}',
    botName: '${selectedBot?.name || 'Asistente'}',
    apiBaseUrl: 'http://localhost:8000',
    primaryColor: '#3b82f6',
    position: 'bottom-right'
  });
</script>`;

  const copyToClipboard = () => {
    navigator.clipboard.writeText(embedCode);
    alert('Código copiado al portapapeles');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Chat Widget</h1>
        <p className="mt-2 text-gray-600">
          Prueba y configura el widget de chat embebible
        </p>
      </div>

      {/* Configuration */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Configuración del Widget
        </h2>

        <div className="space-y-4">
          {/* Bot Selector */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Seleccionar Bot
            </label>
            <select
              value={selectedBotId}
              onChange={(e) => {
                setSelectedBotId(e.target.value);
                setShowWidget(false);
              }}
              className="w-full md:w-96 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              {bots.map((bot) => (
                <option key={bot.bot_id} value={bot.bot_id}>
                  {bot.name} ({bot.bot_id})
                </option>
              ))}
            </select>
          </div>

          {/* Bot Info */}
          {selectedBot && (
            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="font-medium text-gray-900 mb-2">{selectedBot.name}</h3>
              <p className="text-sm text-gray-600 mb-2">{selectedBot.description}</p>
              <div className="flex gap-4 text-xs text-gray-500">
                <span>ID: {selectedBot.bot_id}</span>
                <span>Temperature: {selectedBot.temperature}</span>
                <span>Retrieval K: {selectedBot.retrieval_k}</span>
              </div>
            </div>
          )}

          {/* Show Widget Button */}
          <div>
            <button
              onClick={() => setShowWidget(!showWidget)}
              className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              {showWidget ? 'Ocultar Widget' : 'Mostrar Widget'}
            </button>
          </div>
        </div>
      </div>

      {/* Embed Code */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Código de Embebido
        </h2>
        <p className="text-sm text-gray-600 mb-4">
          Copia este código y pégalo en el HTML de tu sitio web, justo antes del cierre de la etiqueta {'</body>'}
        </p>

        <div className="relative">
          <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
            <code>{embedCode}</code>
          </pre>
          <button
            onClick={copyToClipboard}
            className="absolute top-2 right-2 px-3 py-1 bg-gray-700 text-white text-xs rounded hover:bg-gray-600 transition-colors"
          >
            Copiar
          </button>
        </div>

        <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex gap-2">
            <span className="text-blue-600">ℹ️</span>
            <div className="text-sm text-blue-800">
              <p className="font-medium">Cómo usar el widget:</p>
              <div className="mt-1 space-y-1">
                <p>1. <strong>Desarrollo:</strong> Ejecuta <code className="bg-blue-100 px-1 rounded">npm run widget:dev</code> y abre <code className="bg-blue-100 px-1 rounded">http://localhost:5176/index-widget.html</code></p>
                <p>2. <strong>Producción:</strong> Ejecuta <code className="bg-blue-100 px-1 rounded">npm run widget:build</code> y despliega <code className="bg-blue-100 px-1 rounded">dist-widget/widget.iife.js</code> a tu CDN</p>
                <p>3. Ver documentación completa en <code className="bg-blue-100 px-1 rounded">frontend/WIDGET_README.md</code></p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* React Component Usage */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Uso como Componente React
        </h2>
        <p className="text-sm text-gray-600 mb-4">
          Si tu sitio web usa React, puedes importar el componente directamente:
        </p>

        <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
          <code>{`import ChatWidget from './components/ChatWidget';

function App() {
  return (
    <div>
      {/* Tu contenido aquí */}

      <ChatWidget
        botId="${selectedBotId}"
        botName="${selectedBot?.name || 'Asistente'}"
        apiBaseUrl="http://localhost:8000"
        primaryColor="#3b82f6"
        position="bottom-right"
      />
    </div>
  );
}`}</code>
        </pre>
      </div>

      {/* Instructions */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Instrucciones de Configuración
        </h2>
        <div className="space-y-3 text-sm text-gray-600">
          <div className="flex gap-3">
            <span className="font-semibold text-gray-900">1.</span>
            <p>
              <strong>botId:</strong> El ID único del bot que quieres usar (obligatorio)
            </p>
          </div>
          <div className="flex gap-3">
            <span className="font-semibold text-gray-900">2.</span>
            <p>
              <strong>botName:</strong> El nombre que se mostrará en el encabezado del chat (opcional, por defecto: "Asistente")
            </p>
          </div>
          <div className="flex gap-3">
            <span className="font-semibold text-gray-900">3.</span>
            <p>
              <strong>apiBaseUrl:</strong> La URL de tu backend API (opcional, por defecto: "http://localhost:8000")
            </p>
          </div>
          <div className="flex gap-3">
            <span className="font-semibold text-gray-900">4.</span>
            <p>
              <strong>primaryColor:</strong> Color principal del widget en formato hexadecimal (opcional, por defecto: "#3b82f6")
            </p>
          </div>
          <div className="flex gap-3">
            <span className="font-semibold text-gray-900">5.</span>
            <p>
              <strong>position:</strong> Posición del widget: "bottom-right" o "bottom-left" (opcional, por defecto: "bottom-right")
            </p>
          </div>
        </div>
      </div>

      {/* Widget Preview */}
      {showWidget && (
        <ChatWidget
          botId={selectedBotId}
          botName={selectedBot?.name}
          apiBaseUrl="http://localhost:8000"
          primaryColor="#3b82f6"
          position="bottom-right"
        />
      )}
    </div>
  );
}
