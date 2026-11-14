'use client';

import { ChevronRight, ImageIcon } from 'lucide-react';
import Link from 'next/link';
import { useEffect, useState } from 'react';
import DoadoLockerBadge from '@/components/DoadoLockerBadge';
import api, { API_BASE_URL } from '@/services/api';

interface AnuncioResumo {
  id: number;
  titulo: string;
  tipo: string;
  status: string;
  doado_via_locker: boolean;
  imagens: { url: string }[];
}

const STATUS: Record<string, { label: string; cor: string }> = {
  disponivel: { label: 'Disponível', cor: 'bg-emerald-50 text-emerald-700' },
  reservado: { label: 'Reservado', cor: 'bg-amber-50 text-amber-700' },
  doado_trocado: { label: 'Concluído', cor: 'bg-gray-100 text-gray-600' },
};

/** Faixa no topo da conversa mostrando sobre qual item ela é. */
export default function AnuncioContexto({
  anuncioId,
  onCarregado,
}: {
  anuncioId: number;
  onCarregado?: (titulo: string) => void;
}) {
  const [anuncio, setAnuncio] = useState<AnuncioResumo | null>(null);

  useEffect(() => {
    api
      .get<AnuncioResumo>(`/anuncios/${anuncioId}`)
      .then(({ data }) => {
        setAnuncio(data);
        onCarregado?.(data.titulo);
      })
      .catch(() => setAnuncio(null));
    // onCarregado só precisa rodar na primeira carga do anúncio
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [anuncioId]);

  if (!anuncio) return null;

  const foto = anuncio.imagens[0]?.url;
  const fotoUrl = foto ? (foto.startsWith('http') ? foto : `${API_BASE_URL}${foto}`) : null;
  const status = STATUS[anuncio.status];

  return (
    <Link
      href={`/anuncios/${anuncio.id}`}
      className='group flex items-center gap-3 border-b border-gray-200 bg-white px-4 py-2.5 transition-colors hover:bg-gray-50'
    >
      <span className='flex h-12 w-12 shrink-0 items-center justify-center overflow-hidden rounded-lg bg-gray-100'>
        {fotoUrl ? (
          <img src={fotoUrl} alt='' width={48} height={48} className='h-full w-full object-cover' />
        ) : (
          <ImageIcon size={20} className='text-gray-400' aria-hidden='true' />
        )}
      </span>
      <span className='min-w-0 flex-1'>
        <span className='block truncate text-xs text-gray-500'>Sobre o item</span>
        <span className='block truncate text-sm font-semibold text-gray-900'>{anuncio.titulo}</span>
      </span>
      {anuncio.doado_via_locker ? (
        <DoadoLockerBadge />
      ) : (
        status && <span className={`shrink-0 rounded-full px-2 py-0.5 text-xs font-medium ${status.cor}`}>{status.label}</span>
      )}
      <ChevronRight size={18} className='shrink-0 text-gray-400 transition-transform group-hover:translate-x-0.5' aria-hidden='true' />
    </Link>
  );
}
