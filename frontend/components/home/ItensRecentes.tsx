'use client';

import { ArrowRight } from 'lucide-react';
import Link from 'next/link';
import { useEffect, useState } from 'react';
import AnuncioCard, { type Anuncio } from '@/components/AnuncioCard';
import api from '@/services/api';

export default function ItensRecentes() {
  // null = carregando
  const [anuncios, setAnuncios] = useState<Anuncio[] | null>(null);
  const [erro, setErro] = useState(false);

  useEffect(() => {
    api
      .get<Anuncio[]>('/anuncios/?status=disponivel&limit=4', { timeout: 8000 })
      .then(({ data }) => setAnuncios(data))
      .catch(() => setErro(true));
  }, []);

  // API fora do ar ou nenhum item disponível: a seção some em vez de aparecer vazia
  if (erro || anuncios?.length === 0) return null;

  return (
    <section className="mx-auto max-w-5xl px-4 py-16">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wider text-green-600">
            Disponível agora
          </p>
          <h2 className="mt-2 text-2xl font-bold sm:text-3xl">Itens esperando um novo dono</h2>
        </div>
        <Link
          href="/anuncios"
          className="group inline-flex items-center gap-1 font-semibold text-green-700 hover:text-green-800"
        >
          Ver todos os anúncios
          <ArrowRight
            size={18}
            aria-hidden="true"
            className="transition-transform group-hover:translate-x-1"
          />
        </Link>
      </div>

      <div className="mt-8 grid justify-items-center gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {anuncios === null
          ? Array.from({ length: 4 }, (_, i) => (
              <div
                key={i}
                className="h-80 w-[272px] rounded-2xl bg-gray-100 motion-safe:animate-pulse"
                aria-hidden="true"
              />
            ))
          : anuncios.map((anuncio) => (
              <Link
                key={anuncio.id}
                href={`/anuncios/${anuncio.id}`}
                className="rounded-2xl focus-visible:ring-4 focus-visible:ring-green-200"
              >
                <AnuncioCard anuncio={anuncio} />
              </Link>
            ))}
      </div>
    </section>
  );
}
