import api from './api';
import type { BotStats, GlobalStats, PopularQuestion } from '../types/index';

export const analyticsService = {
  // Obtener estadísticas de un bot
  getBotStats: async (botId: string, days = 7) => {
    const response = await api.get<{ stats: BotStats }>(`/analytics/bot/${botId}`, {
      params: { days },
    });
    return response.data.stats;
  },

  // Obtener estadísticas globales
  getGlobalStats: async (days = 30) => {
    const response = await api.get<{ stats: GlobalStats }>('/analytics/global', {
      params: { days },
    });
    return response.data.stats;
  },

  // Obtener preguntas populares
  getPopularQuestions: async (botId?: string, limit = 10) => {
    const response = await api.get<{ popular_questions: PopularQuestion[]; total: number }>(
      '/analytics/popular-questions',
      {
        params: {
          ...(botId && { bot_id: botId }),
          limit,
        },
      }
    );
    return response.data;
  },

  // Limpiar datos antiguos
  cleanup: async (daysToKeep = 90) => {
    const response = await api.delete<{ message: string }>('/analytics/cleanup', {
      params: { days_to_keep: daysToKeep },
    });
    return response.data;
  },

  // Nube de palabras
  getWordCloud: async (params?: { bot_id?: string; days?: number; limit?: number }) => {
    const response = await api.get('/analytics/word-cloud', { params });
    return response.data;
  },

  // Análisis de temas
  getQuestionTopics: async (params?: { bot_id?: string; days?: number }) => {
    const response = await api.get('/analytics/question-topics', { params });
    return response.data;
  },

  // Uso de documentos
  getDocumentUsage: async (botId: string, days?: number) => {
    const response = await api.get(`/analytics/document-usage/${botId}`, {
      params: { days },
    });
    return response.data;
  },
};
