import { useState, useRef, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import { chatService } from '../services/chat.service';
import type { ChatMessage } from '../types/index';

interface ChatWidgetProps {
  botId: string;
  botName?: string;
  apiBaseUrl?: string;
  primaryColor?: string;
  position?: 'bottom-right' | 'bottom-left';
}

export default function ChatWidget({
  botId,
  botName = 'Asistente',
  apiBaseUrl = 'http://localhost:8000',
  primaryColor = '#3b82f6',
  position = 'bottom-right',
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

  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingMessageIndex, setStreamingMessageIndex] = useState<number | null>(null);

  const chatMutation = useMutation({
    mutationFn: async (question: string) => {
      setIsStreaming(true);

      // Agregar mensaje del asistente vacío que iremos llenando
      const assistantMessageIndex = messages.length + 1; // +1 porque ya agregamos el mensaje del usuario
      setStreamingMessageIndex(assistantMessageIndex);

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: '',
        },
      ]);

      let fullContent = '';

      try {
        await chatService.sendMessageStream(
          question,
          botId,
          // onChunk: agregar texto progresivamente
          (chunk: string) => {
            fullContent += chunk;
            setMessages((prev) => {
              const newMessages = [...prev];
              newMessages[assistantMessageIndex] = {
                role: 'assistant',
                content: fullContent,
              };
              return newMessages;
            });
          },
          // onMetadata: opcional, podrías guardar las fuentes
          undefined,
          // onError
          (error: string) => {
            setMessages((prev) => {
              const newMessages = [...prev];
              newMessages[assistantMessageIndex] = {
                role: 'assistant',
                content: `Error: ${error}`,
              };
              return newMessages;
            });
          },
          // onDone
          () => {
            setIsStreaming(false);
            setStreamingMessageIndex(null);
          }
        );
      } catch (error: any) {
        console.error('Streaming error:', error);
        setMessages((prev) => {
          const newMessages = [...prev];
          newMessages[assistantMessageIndex] = {
            role: 'assistant',
            content: 'Lo siento, ha ocurrido un error. Por favor, intenta nuevamente.',
          };
          return newMessages;
        });
        setIsStreaming(false);
        setStreamingMessageIndex(null);
      }
    },
  });

  const handleSend = () => {
    if (!input.trim() || chatMutation.isPending || isStreaming) return;

    const userMessage = input.trim();
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
    setInput('');
    chatMutation.mutate(userMessage);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const positionClasses =
    position === 'bottom-right' ? 'right-4 bottom-4' : 'left-4 bottom-4';

  return (
    <div className={`fixed ${positionClasses} z-50`}>
      {/* Chat Window */}
      {isOpen && (
        <div className="mb-4 w-96 h-[500px] bg-white rounded-lg shadow-2xl flex flex-col overflow-hidden">
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
                <p className="text-xs opacity-90">En línea</p>
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
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                <div
                  className={`max-w-[80%] rounded-lg p-3 ${
                    message.role === 'user'
                      ? 'text-white'
                      : 'bg-white text-gray-900 shadow'
                  }`}
                  style={
                    message.role === 'user'
                      ? { backgroundColor: primaryColor }
                      : {}
                  }
                >
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                </div>
              </div>
            ))}
            {(chatMutation.isPending || isStreaming) && streamingMessageIndex === null && (
              <div className="flex justify-start">
                <div className="bg-white rounded-lg p-3 shadow">
                  <div className="flex gap-1">
                    <div
                      className="w-2 h-2 rounded-full animate-bounce"
                      style={{ backgroundColor: primaryColor, animationDelay: '0ms' }}
                    ></div>
                    <div
                      className="w-2 h-2 rounded-full animate-bounce"
                      style={{ backgroundColor: primaryColor, animationDelay: '150ms' }}
                    ></div>
                    <div
                      className="w-2 h-2 rounded-full animate-bounce"
                      style={{ backgroundColor: primaryColor, animationDelay: '300ms' }}
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
                disabled={chatMutation.isPending || isStreaming}
              />
              <button
                onClick={handleSend}
                disabled={!input.trim() || chatMutation.isPending || isStreaming}
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
