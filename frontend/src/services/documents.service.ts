import api from './api';
import type { Document } from '../types';

export const documentsService = {
  // Subir un documento
  upload: async (file: File, botId: string) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post<{
      message: string;
      document: {
        id: string;
        filename: string;
        path: string;
        chunks: number;
      };
    }>(`/documents/upload?bot_id=${botId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  },

  // Listar documentos
  list: async (botId?: string) => {
    const response = await api.get<{ documents: Document[]; total: number }>(
      '/documents/list',
      {
        params: botId ? { bot_id: botId } : {},
      }
    );
    return response.data.documents;
  },

  // Eliminar un documento
  delete: async (docId: string) => {
    const response = await api.delete<{ message: string; doc_id: string }>(
      `/documents/${docId}`
    );
    return response.data;
  },

  // Mover un documento a otro bot
  moveToBot: async (docId: string, newBotId: string) => {
    const response = await api.patch<{
      message: string;
      doc_id: string;
      new_bot_id: string;
    }>(`/documents/${docId}/move`, null, {
      params: { new_bot_id: newBotId },
    });
    return response.data;
  },
};
