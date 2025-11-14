// Auth Types - Archivo separado para forzar recarga de módulos

export enum UserRole {
  ADMIN = 'admin',
  OWNER = 'owner',
  EDITOR = 'editor',
  VIEWER = 'viewer'
}

export interface User {
  user_id: string;
  email: string;
  username: string;
  role: UserRole;
  organization_id: string | null;
  active: boolean;
  created_at: string;
  updated_at: string;
  allowed_bots: string[] | null;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
  role?: UserRole;
  organization_id?: string;
  allowed_bots?: string[];
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}
