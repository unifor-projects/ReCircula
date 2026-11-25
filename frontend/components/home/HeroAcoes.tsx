'use client';

import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';

const BTN = 'rounded-xl px-6 py-3 text-center font-semibold transition active:scale-[0.98]';

export default function HeroAcoes() {
  const { isAuthenticated } = useAuth();

  return (
    <div className='mt-8 flex w-full flex-col gap-3 sm:w-auto sm:flex-row'>
      <Link href='/anuncios' className={`${BTN} bg-green-600 text-white shadow-md hover:-translate-y-0.5 hover:bg-green-700`}>
        Explorar anúncios
      </Link>
      {isAuthenticated ? (
        <Link href='/anuncios/novo' className={`${BTN} border border-gray-300 bg-white text-gray-800 hover:-translate-y-0.5 hover:bg-gray-50`}>
          Anunciar um item
        </Link>
      ) : (
        <Link href='/register' className={`${BTN} border border-gray-300 bg-white text-gray-800 hover:-translate-y-0.5 hover:bg-gray-50`}>
          Criar conta grátis
        </Link>
      )}
    </div>
  );
}
