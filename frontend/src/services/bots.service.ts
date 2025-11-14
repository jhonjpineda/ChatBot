import api from './api';
import type { Bot, BotCreate, BotUpdate } from '../types/index';

export const botsService = {
  // Listar todos los bots
  list: async (activeOnly = false) => {
    const response = await api.get<{ bots: Bot[]; total: number }>('/bots/', {
      params: { active_only: activeOnly },
    });
    return response.data;
  },

  // Obtener un bot específico
  get: async (botId: string) => {
    const response = await api.get<{ bot: Bot }>(`/bots/${botId}`);
    return response.data.bot;
  },

  // Crear un nuevo bot
  create: async (data: BotCreate) => {
    const response = await api.post<{ message: string; bot: Bot }>('/bots/', data);
    return response.data;
  },

  // Actualizar un bot
  update: async (botId: string, data: BotUpdate) => {
    const response = await api.put<{ message: string; bot: Bot }>(`/bots/${botId}`, data);
    return response.data;
  },

  // Eliminar un bot
  delete: async (botId: string) => {
    const response = await api.delete<{ message: string; bot_id: string }>(`/bots/${botId}`);
    return response.data;
  },

  // Obtener prompts predefinidos
  getPresets: async () => {
    const response = await api.get<{ presets: Record<string, string>; available: string[] }>(
      '/bots/presets/prompts'
    );
    return response.data;
  },
};
