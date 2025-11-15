/**
 * Hook para streaming de respuestas con Server-Sent Events (SSE)
 * Maneja conexión, recepción de chunks y estado del streaming
 */
import { useState, useCallback } from 'react';

interface Source {
  text: string;
  similarity: number;
  metadata: Record<string, any>;
  distance?: number;
}

interface BotConfig {
  bot_id: string;
  name: string;
  temperature: number;
  strict_mode?: boolean;
  threshold?: number;
  sources_found?: number;
}

interface StreamMessage {
  text: string;
  sources: Source[];
  botConfig: BotConfig | null;
  isComplete: boolean;
  isFallback: boolean;
}

interface UseStreamChatReturn {
  message: StreamMessage;
  isStreaming: boolean;
  error: string | null;
  streamChat: (question: string, botId: string) => Promise<void>;
  reset: () => void;
}

/**
 * Hook para manejar streaming de chat con SSE
 *
 * @example
 * ```tsx
 * const { message, isStreaming, error, streamChat } = useStreamChat();
 *
 * const handleSubmit = async () => {
 *   await streamChat("¿Cómo reinicio el router?", "soporte-tech");
 * };
 *
 * return (
 *   <div>
 *     <p>{message.text}</p>
 *     {isStreaming && <span>Escribiendo...</span>}
 *   </div>
 * );
 * ```
 */
export function useStreamChat(): UseStreamChatReturn {
  const [message, setMessage] = useState<StreamMessage>({
    text: '',
    sources: [],
    botConfig: null,
    isComplete: false,
    isFallback: false,
  });
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const reset = useCallback(() => {
    setMessage({
      text: '',
      sources: [],
      botConfig: null,
      isComplete: false,
      isFallback: false,
    });
    setError(null);
    setIsStreaming(false);
  }, []);

  const streamChat = useCallback(async (question: string, botId: string) => {
    // Reset estado previo
    setIsStreaming(true);
    setError(null);
    setMessage({
      text: '',
      sources: [],
      botConfig: null,
      isComplete: false,
      isFallback: false,
    });

    try {
      const response = await fetch('http://localhost:8000/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question,
          bot_id: botId,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      if (!response.body) {
        throw new Error('Response body is null');
      }

      // Leer stream usando ReadableStream API
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          break;
        }

        // Decodificar chunk
        buffer += decoder.decode(value, { stream: true });

        // Procesar líneas completas (SSE usa \n\n como separador)
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // Guardar línea incompleta

        for (const line of lines) {
          // SSE format: "data: {json}"
          if (line.startsWith('data: ')) {
            try {
              const jsonStr = line.slice(6); // Remover "data: "
              const data = JSON.parse(jsonStr);

              // Manejar diferentes tipos de mensajes
              if (data.type === 'metadata') {
                // Metadata inicial con fuentes y config
                setMessage(prev => ({
                  ...prev,
                  sources: data.sources || [],
                  botConfig: data.bot_config || null,
                }));
              } else if (data.type === 'chunk') {
                // Chunk de texto
                setMessage(prev => ({
                  ...prev,
                  text: prev.text + data.content,
                }));
              } else if (data.type === 'done') {
                // Finalización
                setMessage(prev => ({
                  ...prev,
                  isComplete: true,
                  isFallback: data.fallback || false,
                }));
              } else if (data.type === 'error') {
                // Error del servidor
                setError(data.message || 'Error desconocido');
              }
            } catch (parseError) {
              console.error('Error parsing SSE data:', parseError, 'Line:', line);
            }
          }
        }
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error desconocido';
      setError(errorMessage);
      console.error('Streaming error:', err);
    } finally {
      setIsStreaming(false);
    }
  }, []);

  return {
    message,
    isStreaming,
    error,
    streamChat,
    reset,
  };
}
