/**
 * Servicio para gestión de aprobación de usuarios
 * Endpoints: /auth/users/pending/*, /auth/users/{id}/approve, /auth/users/{id}/reject
 */
import api from './api';

export interface PendingUser {
  user_id: string;
  email: string;
  username: string;
  role: string;
  created_at: string;
  hours_waiting: number;
}

export interface PendingCountResponse {
  pending_count: number;
}

class ApprovalService {
  /**
   * Obtiene lista de usuarios pendientes de aprobación
   */
  async getPendingUsers(): Promise<PendingUser[]> {
    const response = await api.get<PendingUser[]>('/auth/users/pending/list');
    return response.data;
  }

  /**
   * Obtiene el contador de usuarios pendientes
   */
  async getPendingCount(): Promise<number> {
    const response = await api.get<PendingCountResponse>('/auth/users/pending/count');
    return response.data.pending_count;
  }

  /**
   * Aprueba un usuario pendiente
   */
  async approveUser(userId: string): Promise<void> {
    await api.post(`/auth/users/${userId}/approve`);
  }

  /**
   * Rechaza y elimina un usuario pendiente
   */
  async rejectUser(userId: string): Promise<void> {
    await api.post(`/auth/users/${userId}/reject`);
  }
}

export const approvalService = new ApprovalService();
