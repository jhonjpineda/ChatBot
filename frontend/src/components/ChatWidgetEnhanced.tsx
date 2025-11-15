/**
 * ChatWidget mejorado con streaming usando hook useStreamChat
 * Incluye:
 * - Streaming en tiempo real con SSE
 * - Cursor parpadeante mientras escribe
 * - Mostrar fuentes usadas
 * - Badge de fallback cuando no hay docs
 * - Mejor manejo de errores
 */
import { useState, useRef, useEffect } from 'react';
import { useStreamChat } from '../hooks/useStreamChat';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  sources?: any[];
  isFallback?: boolean;
}

interface ChatWidgetProps {
  botId: string;
  botName?: string;
  primaryColor?: string;
  position?: 'bottom-right' | 'bottom-left';
  showSources?: boolean;
}

export default function ChatWidgetEnhanced({
  botId,
  botName = 'Asistente',
  primaryColor = '#3b82f6',
  position = 'bottom-right',
  showSources = true,
}: ChatWidgetProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content: `¡Hola! Soy ${botName}. ¿En qué puedo ayudarte?`,
    },
  ]);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { message, isStreaming, error, streamChat, reset } = useStreamChat();

  const handleSend = async () => {
    if (!input.trim() || isStreaming) return;

    const userMessage = input.trim();

    // Agregar mensaje del usuario
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
    setInput('');

    // Resetear estado previo del hook
    reset();

    // Iniciar streaming
    await streamChat(userMessage, botId);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Actualizar mensajes cuando el streaming completa
  useEffect(() => {
    if (message.isComplete && message.text) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: message.text,
          sources: message.sources,
          isFallback: message.isFallback,
        },
      ]);
    }
  }, [message.isComplete]);

  // Actualizar mensajes cuando hay error
  useEffect(() => {
    if (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `Error: ${error}`,
        },
      ]);
    }
  }, [error]);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, message.text]);

  const positionClasses =
    position === 'bottom-right' ? 'right-4 bottom-4' : 'left-4 bottom-4';

  return (
    <div className={`fixed ${positionClasses} z-50`}>
      {/* Chat Window */}
      {isOpen && (
        <div className="mb-4 w-96 h-[600px] bg-white rounded-lg shadow-2xl flex flex-col overflow-hidden">
          {/* Header */}
          <div
            className="p-4 text-white flex items-center justify-between"
            style={{ backgroundColor: primaryColor }}
          >
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
                🤖
              </div>
              <div>
                <h3 className="font-semibold">{botName}</h3>
                <p className="text-xs opacity-90">
                  {isStreaming ? 'Escribiendo...' : 'En línea'}
                </p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="text-white hover:bg-white hover:bg-opacity-20 rounded-full p-1 transition-colors"
            >
              <svg
                className="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`flex ${
                  msg.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                <div className="max-w-[85%]">
                  <div
                    className={`rounded-lg p-3 ${
                      msg.role === 'user'
                        ? 'text-white'
                        : 'bg-white text-gray-900 shadow'
                    }`}
                    style={
                      msg.role === 'user'
                        ? { backgroundColor: primaryColor }
                        : {}
                    }
                  >
                    <p className="text-sm whitespace-pre-wrap leading-relaxed">
                      {msg.content}
                    </p>
                  </div>

                  {/* Fallback badge */}
                  {msg.isFallback && (
                    <div className="mt-2 inline-flex items-center gap-1 px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded">
                      ℹ️ Sin información en documentos
                    </div>
                  )}

                  {/* Sources */}
                  {showSources && msg.sources && msg.sources.length > 0 && (
                    <div className="mt-2 p-2 bg-gray-100 rounded text-xs">
                      <p className="font-semibold text-gray-700 mb-1">
                        📚 Fuentes ({msg.sources.length}):
                      </p>
                      {msg.sources.slice(0, 3).map((source, i) => (
                        <div
                          key={i}
                          className="mt-1 pl-2 border-l-2 border-gray-300"
                        >
                          <p className="text-gray-600">
                            Similitud: {(source.similarity * 100).toFixed(0)}%
                          </p>
                          <p className="text-gray-500 truncate">
                            {source.text.slice(0, 80)}...
                          </p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {/* Streaming message */}
            {isStreaming && message.text && (
              <div className="flex justify-start">
                <div className="max-w-[85%]">
                  <div className="bg-white text-gray-900 shadow rounded-lg p-3">
                    <p className="text-sm whitespace-pre-wrap leading-relaxed">
                      {message.text}
                      {/* Cursor parpadeante */}
                      <span className="inline-block w-0.5 h-4 bg-gray-900 ml-0.5 animate-pulse" />
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Loading indicator (antes de recibir primer chunk) */}
            {isStreaming && !message.text && (
              <div className="flex justify-start">
                <div className="bg-white rounded-lg p-3 shadow">
                  <div className="flex gap-1">
                    <div
                      className="w-2 h-2 rounded-full animate-bounce"
                      style={{
                        backgroundColor: primaryColor,
                        animationDelay: '0ms',
                      }}
                    ></div>
                    <div
                      className="w-2 h-2 rounded-full animate-bounce"
                      style={{
                        backgroundColor: primaryColor,
                        animationDelay: '150ms',
                      }}
                    ></div>
                    <div
                      className="w-2 h-2 rounded-full animate-bounce"
                      style={{
                        backgroundColor: primaryColor,
                        animationDelay: '300ms',
                      }}
                    ></div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="p-4 bg-white border-t border-gray-200">
            <div className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Escribe tu mensaje..."
                className="flex-1 px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:border-transparent"
                style={{
                  '--tw-ring-color': primaryColor,
                } as React.CSSProperties}
                disabled={isStreaming}
              />
              <button
                onClick={handleSend}
                disabled={!input.trim() || isStreaming}
                className="px-4 py-2 text-white rounded-full hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-opacity"
                style={{ backgroundColor: primaryColor }}
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                  />
                </svg>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-14 h-14 rounded-full text-white shadow-lg hover:shadow-xl transition-all flex items-center justify-center"
        style={{ backgroundColor: primaryColor }}
      >
        {isOpen ? (
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        ) : (
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
            />
          </svg>
        )}
      </button>
    </div>
  );
}
