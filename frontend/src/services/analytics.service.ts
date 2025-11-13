import api from './api';
import type { BotStats, GlobalStats, PopularQuestion } from '../types';

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
};
