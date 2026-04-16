import { jwtVerify } from 'jose';
import type { JWTPayload } from 'jose';
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const PUBLIC_ROUTES = ['/login', '/register', '/forgot-password', '/reset-password', '/verify-email', '/perfil'];
const SESSION_COOKIE_NAME = process.env.NEXT_SERVER_SESSION_COOKIE_NAME ?? 'rc_session';
const JWT_SECRET_KEY = process.env.JWT_SECRET_KEY;

function isPublicRoute(pathname: string): boolean {
  return PUBLIC_ROUTES.some((route) => pathname === route || pathname.startsWith(`${route}/`));
}

async function hasValidSessionToken(request: NextRequest): Promise<boolean> {
  const sessionToken = request.cookies.get(SESSION_COOKIE_NAME)?.value;
  if (!sessionToken || !JWT_SECRET_KEY) {
    return false;
  }

  try {
    const { payload } = await jwtVerify(sessionToken, new TextEncoder().encode(JWT_SECRET_KEY), {
      algorithms: ['HS256'],
    });

    return payload.type === 'access' && typeof payload.sub === 'string' && isNotExpired(payload);
  } catch {
    return false;
  }
}

function isNotExpired(payload: JWTPayload): boolean {
  if (typeof payload.exp !== 'number') return false;
  return payload.exp * 1000 > Date.now();
}

export async function middleware(request: NextRequest) {
  if (isPublicRoute(request.nextUrl.pathname)) {
    return NextResponse.next();
  }

  const hasValidSession = await hasValidSessionToken(request);
  if (!hasValidSession) {
    const loginUrl = new URL('/login', request.url);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};
