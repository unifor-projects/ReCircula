export interface User {
  id: number;
  name: string;
  email: string;
  created_at: string;
}

export interface Announcement {
  id: number;
  title: string;
  description: string;
  category: string;
  status: 'available' | 'reserved' | 'donated';
  user_id: number;
  created_at: string;
  images: string[];
}

export interface ApiError {
  detail: string;
}
