import { io, Socket } from 'socket.io-client';

const BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  (process.env.NODE_ENV !== 'production' ? 'http://localhost:8000' : undefined);

let socket: Socket | null = null;

export function getSocket(): Socket | null {
  return socket;
}

export function connectSocket(token: string): Socket {
  if (socket) {
    // Keep the existing socket (reconnection is automatic).
    // Update auth so the next reconnect uses the latest token.
    socket.auth = { token };
    return socket;
  }

  socket = io(BASE_URL!, {
    path: '/socket.io',
    auth: { token },
    transports: ['websocket', 'polling'],
    reconnection: true,
    reconnectionDelay: 1000,
    reconnectionDelayMax: 10000,
    reconnectionAttempts: Infinity,
  });

  return socket;
}

export function disconnectSocket(): void {
  if (socket) {
    socket.disconnect();
    socket = null;
  }
}
