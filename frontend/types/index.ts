export interface User {
  id: number;
  nome: string;
  email: string;
  foto_url: string | null;
  descricao: string | null;
  localizacao: string | null;
  cep: string | null;
  is_active: boolean;
  is_admin: boolean;
  email_verificado: boolean;
  criado_em: string;
  atualizado_em: string;
}

export interface ApiError {
  detail: string;
}
