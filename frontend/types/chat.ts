export interface ChatParticipant {
  id: number;
  user_id: number;
  joined_at: string;
  last_read_at: string | null;
  user: {
    id: number;
    nome: string;
    foto_url: string | null;
    localizacao: string | null;
    criado_em: string;
  };
}

export interface ChatMessage {
  id: number;
  conversation_id: number;
  sender_id: number;
  content: string;
  created_at: string;
  sender: {
    id: number;
    nome: string;
    foto_url: string | null;
    localizacao: string | null;
    criado_em: string;
  };
}

export interface ChatConversation {
  id: number;
  type: 'direct' | 'group';
  name: string | null;
  created_at: string;
  participants: ChatParticipant[];
  last_message: ChatMessage | null;
  unread_count: number;
}

export interface TypingUser {
  user_id: number;
  username: string;
  conversation_id: number;
}

export interface UserSearchResult {
  id: number;
  nome: string;
  foto_url: string | null;
  localizacao: string | null;
}
