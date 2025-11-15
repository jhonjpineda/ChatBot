// Types para la aplicación

export interface Bot {
  bot_id: string;
  name: string;
  description?: string;
  system_prompt: string;
  temperature: number;
  max_tokens?: number;
  retrieval_k: number;
  active: boolean;
  created_at: string;
  updated_at: string;
  metadata?: Record<string, any>;
}

export interface BotCreate {
  bot_id: string;
  name: string;
  description?: string;
  system_prompt?: string;
  temperature?: number;
  retrieval_k?: number;
  metadata?: Record<string, any>;
}

export interface BotUpdate {
  name?: string;
  description?: string;
  system_prompt?: string;
  temperature?: number;
  retrieval_k?: number;
  active?: boolean;
  metadata?: Record<string, any>;
}

export interface Document {
  doc_id: string;
  bot_id: string;
  filename: string;
  uploaded_at: string;
  file_type?: string;
  chunks?: number;
}

export interface ChatMessage {
  question: string;
  bot_id: string;
}

export interface ChatResponse {
  answer: string;
  sources: Array<{
    text: string;
    metadata: Record<string, any>;
    score?: number;
  }>;
  bot_config: {
    bot_id: string;
    name: string;
    temperature: number;
  };
}

export interface BotStats {
  bot_id: string;
  period_days: number;
  total_interactions: number;
  success_rate: number;
  avg_response_time_ms: number;
  avg_sources_count: number;
  avg_question_length: number;
  avg_answer_length: number;
  daily_breakdown: Array<{
    date: string;
    count: number;
  }>;
}

export interface GlobalStats {
  period_days: number;
  total_interactions: number;
  total_bots_used: number;
  success_rate: number;
  interactions_by_bot: Record<string, number>;
  avg_response_time_ms: number;
  daily_breakdown: Array<{
    date: string;
    count: number;
  }>;
}

export interface PopularQuestion {
  question_sample: string;
  count: number;
  avg_response_time_ms: number;
}

// Auth Types
export const UserRole = {
  ADMIN: 'admin',
  OWNER: 'owner',
  EDITOR: 'editor',
  VIEWER: 'viewer'
} as const;

export type UserRoleType = typeof UserRole[keyof typeof UserRole];

export interface User {
  user_id: string;
  email: string;
  username: string;
  role: UserRoleType;
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
  role?: UserRoleType;
  organization_id?: string;
  allowed_bots?: string[];
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}
