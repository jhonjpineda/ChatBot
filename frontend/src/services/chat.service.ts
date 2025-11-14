import api from './api';
import type { ChatResponse } from '../types';

export const chatService = {
  // Enviar mensaje al bot (sin streaming)
  sendMessage: async (question: string, botId: string = 'default') => {
    const response = await api.post<ChatResponse>('/chat/', {
      question,
      bot_id: botId,
    });
    return response.data;
  },

  // Enviar mensaje con streaming (Server-Sent Events)
  sendMessageStream: async (
    question: string,
    botId: string = 'default',
    onChunk: (chunk: string) => void,
    onMetadata?: (metadata: any) => void,
    onError?: (error: string) => void,
    onDone?: () => void
  ) => {
    const response = await fetch(`${api.defaults.baseURL}/chat/stream`, {
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

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) {
      throw new Error('No reader available');
    }

    let buffer = '';

    try {
      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          break;
        }

        // Decodificar y agregar al buffer
        buffer += decoder.decode(value, { stream: true });

        // Procesar líneas completas
        const lines = buffer.split('\n');

        // Mantener la última línea incompleta en el buffer
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.trim().startsWith('data: ')) {
            try {
              const jsonStr = line.trim().slice(6);
              const data = JSON.parse(jsonStr);

              if (data.type === 'metadata' && onMetadata) {
                onMetadata(data);
              } else if (data.type === 'chunk') {
                onChunk(data.content);
              } else if (data.type === 'error' && onError) {
                onError(data.message);
              } else if (data.type === 'done' && onDone) {
                onDone();
              }
            } catch (e) {
              console.error('Error parsing JSON:', e, 'Line:', line);
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  },
};
