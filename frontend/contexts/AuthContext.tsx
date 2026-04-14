'use client';

import { useRouter } from 'next/navigation';
import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
  useCallback,
} from 'react';
import { User } from '@/types';
import { authClient } from '@/services/authClient';

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (accessToken: string, refreshToken: string, user: User) => void;
  logout: () => Promise<void>;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);
const ACCESS_TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';
const USER_KEY = 'user';
const REFRESH_BUFFER_MS = 60_000;

function getTokenExpirationMs(token: string): number | null {
  const [, payload] = token.split('.');
  if (!payload) return null;

  try {
    // JWT uses base64url encoding. Convert to standard base64 and pad to a multiple of 4.
    const base64Payload = payload.replace(/-/g, '+').replace(/_/g, '/');
    const normalizedPayload = base64Payload.padEnd(Math.ceil(base64Payload.length / 4) * 4, '=');
    const decodedPayload = JSON.parse(atob(normalizedPayload)) as { exp?: number };
    if (!decodedPayload.exp) return null;
    return decodedPayload.exp * 1000;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [refreshToken, setRefreshToken] = useState<string | null>(null);

  const clearAuthStorage = useCallback(() => {
    setToken(null);
    setRefreshToken(null);
    setUser(null);
    sessionStorage.removeItem(ACCESS_TOKEN_KEY);
    sessionStorage.removeItem(REFRESH_TOKEN_KEY);
    sessionStorage.removeItem(USER_KEY);
  }, []);

  const persistAuth = useCallback(
    (accessToken: string, nextRefreshToken: string, nextUser: User) => {
      setToken(accessToken);
      setRefreshToken(nextRefreshToken);
      setUser(nextUser);
      sessionStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
      sessionStorage.setItem(REFRESH_TOKEN_KEY, nextRefreshToken);
      sessionStorage.setItem(USER_KEY, JSON.stringify(nextUser));
    },
    []
  );

  useEffect(() => {
    const storedToken = sessionStorage.getItem(ACCESS_TOKEN_KEY);
    const storedRefreshToken = sessionStorage.getItem(REFRESH_TOKEN_KEY);
    const storedUser = sessionStorage.getItem(USER_KEY);
    if (storedToken && storedRefreshToken && storedUser) {
      try {
        const parsedUser = JSON.parse(storedUser) as User;
        setToken(storedToken);
        setRefreshToken(storedRefreshToken);
        setUser(parsedUser);
      } catch {
        clearAuthStorage();
      }
      return;
    }
    clearAuthStorage();
  }, [clearAuthStorage]);

  const refreshAccessToken = useCallback(async () => {
    if (!refreshToken) {
      clearAuthStorage();
      router.replace('/login');
      return;
    }

    try {
      const response = await authClient.post<{ access_token: string }>('/auth/refresh', {
        refresh_token: refreshToken,
      });
      setToken(response.data.access_token);
      sessionStorage.setItem(ACCESS_TOKEN_KEY, response.data.access_token);
    } catch {
      clearAuthStorage();
      router.replace('/login');
    }
  }, [clearAuthStorage, refreshToken, router]);

  useEffect(() => {
    if (!token || !refreshToken) return;

    const expiresAt = getTokenExpirationMs(token);
    if (!expiresAt) {
      clearAuthStorage();
      router.replace('/login');
      return;
    }

    const timeUntilRefreshMs = expiresAt - Date.now() - REFRESH_BUFFER_MS;
    if (timeUntilRefreshMs <= 0) {
      // Token is already expired or expiring within the buffer window — refresh immediately.
      void refreshAccessToken();
      return;
    }

    const timeoutId = window.setTimeout(() => {
      void refreshAccessToken();
    }, timeUntilRefreshMs);
    return () => window.clearTimeout(timeoutId);
  }, [clearAuthStorage, refreshAccessToken, refreshToken, router, token]);

  const login = useCallback(
    (accessToken: string, newRefreshToken: string, newUser: User) => {
      persistAuth(accessToken, newRefreshToken, newUser);
    },
    [persistAuth]
  );

  const logout = useCallback(async () => {
    const currentRefreshToken = refreshToken ?? sessionStorage.getItem(REFRESH_TOKEN_KEY);
    if (currentRefreshToken) {
      try {
        await authClient.post('/auth/logout', { refresh_token: currentRefreshToken });
      } catch {
        // Logout local mesmo quando a sessão remota já estiver inválida.
      }
    }
    clearAuthStorage();
    router.replace('/login');
  }, [clearAuthStorage, refreshToken, router]);

  return (
    <AuthContext.Provider value={{ user, token, login, logout, isAuthenticated: !!token }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
