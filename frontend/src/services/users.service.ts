import { api } from './api';
import type { User, RegisterRequest } from '../types/index';

export interface UserUpdateRequest {
  username?: string;
  role?: string;
  active?: boolean;
  allowed_bots?: string[] | null;
}

class UsersService {
  /**
   * Obtener lista de usuarios
   */
  async getUsers(): Promise<User[]> {
    const response = await api.get<User[]>('/auth/users');
    return response.data;
  }

  /**
   * Obtener usuario por ID
   */
  async getUserById(userId: string): Promise<User> {
    const response = await api.get<User>(`/auth/users/${userId}`);
    return response.data;
  }

  /**
   * Crear nuevo usuario (registro)
   */
  async createUser(data: RegisterRequest): Promise<{ access_token: string; user: User }> {
    const response = await api.post('/auth/register', data);
    return response.data;
  }

  /**
   * Actualizar usuario
   */
  async updateUser(userId: string, data: UserUpdateRequest): Promise<User> {
    const response = await api.patch<User>(`/auth/users/${userId}`, data);
    return response.data;
  }

  /**
   * Eliminar usuario
   */
  async deleteUser(userId: string): Promise<void> {
    await api.delete(`/auth/users/${userId}`);
  }

  /**
   * Desactivar usuario (cambiar active a false)
   */
  async deactivateUser(userId: string): Promise<User> {
    return this.updateUser(userId, { active: false });
  }

  /**
   * Activar usuario (cambiar active a true)
   */
  async activateUser(userId: string): Promise<User> {
    return this.updateUser(userId, { active: true });
  }
}

export const usersService = new UsersService();
