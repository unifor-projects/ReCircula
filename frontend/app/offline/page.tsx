import Link from 'next/link';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Você está offline | ReCircula',
};

export default function OfflinePage() {
  return (
    <div className="flex min-h-[calc(100vh-4rem)] flex-col items-center justify-center gap-4 px-4 text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-full bg-green-100 text-green-600">
        <svg
          className="h-8 w-8"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M18.364 5.636a9 9 0 010 12.728m-3.536-3.536a4 4 0 000-5.656m-3.536-3.536L5.636 18.364M12 12h.01"
          />
        </svg>
      </div>
      <h1 className="text-xl font-bold text-gray-900">Você está sem conexão</h1>
      <p className="max-w-sm text-sm text-gray-600">
        Não foi possível carregar esta página. Verifique sua internet e tente novamente. Páginas
        já visitadas podem continuar disponíveis offline.
      </p>
      <Link
        href="/anuncios"
        className="rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-green-700"
      >
        Tentar novamente
      </Link>
    </div>
  );
}
