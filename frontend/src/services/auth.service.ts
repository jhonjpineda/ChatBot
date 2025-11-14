import { api } from './api';
import { LoginRequest, RegisterRequest, AuthResponse, User } from '../types';

class AuthService {
  private readonly TOKEN_KEY = 'chatbot_token';
  private readonly USER_KEY = 'chatbot_user';

  /**
   * Login de usuario
   */
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>('/auth/login', credentials);
    this.saveAuthData(response.data);
    return response.data;
  }

  /**
   * Registro de nuevo usuario
   */
  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>('/auth/register', data);
    this.saveAuthData(response.data);
    return response.data;
  }

  /**
   * Obtener usuario actual
   */
  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/auth/me');
    this.saveUser(response.data);
    return response.data;
  }

  /**
   * Logout
   */
  logout(): void {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.USER_KEY);
  }

  /**
   * Obtener token almacenado
   */
  getToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  /**
   * Obtener usuario almacenado
   */
  getStoredUser(): User | null {
    const userStr = localStorage.getItem(this.USER_KEY);
    if (!userStr) return null;
    try {
      return JSON.parse(userStr);
    } catch {
      return null;
    }
  }

  /**
   * Verificar si está autenticado
   */
  isAuthenticated(): boolean {
    return this.getToken() !== null;
  }

  /**
   * Guardar datos de autenticación
   */
  private saveAuthData(authData: AuthResponse): void {
    localStorage.setItem(this.TOKEN_KEY, authData.access_token);
    this.saveUser(authData.user);
  }

  /**
   * Guardar usuario
   */
  private saveUser(user: User): void {
    localStorage.setItem(this.USER_KEY, JSON.stringify(user));
  }
}

export const authService = new AuthService();
