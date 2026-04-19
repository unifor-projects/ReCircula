'use client';

import Link from 'next/link';
import { FormEvent, useCallback, useEffect, useRef, useState } from 'react';
import Button from '@/components/Button';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/services/api';
import { PlusIcon } from 'lucide-react';

interface AnuncioImagem {
  id: number;
  url: string;
  ordem: number;
}

interface AnuncioCategoria {
  id: number;
  nome: string;
}

interface AnuncioUsuario {
  id: number;
  nome: string;
  foto_url: string | null;
}

interface Anuncio {
  id: number;
  titulo: string;
  tipo: 'doacao' | 'troca';
  condicao: string;
  status: string;
  localizacao: string | null;
  cep: string | null;
  criado_em: string;
  imagens: AnuncioImagem[];
  categoria: AnuncioCategoria | null;
  usuario: AnuncioUsuario;
}

interface Categoria {
  id: number;
  nome: string;
}

function formatarData(dataISO: string): string {
  const data = new Date(dataISO);
  if (Number.isNaN(data.getTime())) return dataISO;
  return new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  }).format(data);
}

function formatCepInput(value: string): string {
  const digits = value.replace(/\D/g, '').slice(0, 8);
  if (digits.length <= 5) return digits;
  return `${digits.slice(0, 5)}-${digits.slice(5)}`;
}

const TIPO_LABEL: Record<string, string> = {
  doacao: 'Doação',
  troca: 'Troca',
  ambos: 'Doação e Troca',
};
const TIPO_COLOR: Record<string, string> = {
  doacao: 'bg-green-100 text-green-700',
  troca: 'bg-blue-100 text-blue-700',
  ambos: 'bg-purple-100 text-purple-700',
};
const STATUS_LABEL: Record<string, string> = {
  disponivel: 'Disponível',
  reservado: 'Reservado',
  doado_trocado: 'Concluído',
};
const STATUS_COLOR: Record<string, string> = {
  disponivel: 'bg-emerald-50 text-emerald-700',
  reservado: 'bg-amber-50 text-amber-700',
  doado_trocado: 'bg-gray-100 text-gray-500',
};

function AnuncioCard({ anuncio }: { anuncio: Anuncio }) {
  const primeiraImagem = anuncio.imagens[0]?.url ?? null;

  return (
    <article className="min-w-[272px] max-w-[272px] overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm transition-shadow hover:shadow-md">
      <div className="relative h-40 w-full overflow-hidden bg-gray-100">
        {primeiraImagem ? (
          <img src={primeiraImagem} alt={anuncio.titulo} className="h-full w-full object-cover" />
        ) : (
          <div className="flex h-full w-full items-center justify-center">
            <svg
              className="h-12 w-12 text-gray-300"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
          </div>
        )}
        <span
          className={`absolute right-2 top-2 rounded-full px-2 py-0.5 text-xs font-bold ${TIPO_COLOR[anuncio.tipo] ?? 'bg-gray-100 text-gray-600'}`}
        >
          {TIPO_LABEL[anuncio.tipo] ?? anuncio.tipo}
        </span>
      </div>

      <div className="p-4">
        <h3 className="line-clamp-2 text-sm font-semibold text-gray-900">{anuncio.titulo}</h3>

        <div className="mt-2 flex flex-wrap gap-1">
          <span
            className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_COLOR[anuncio.status] ?? 'bg-gray-100 text-gray-600'}`}
          >
            {STATUS_LABEL[anuncio.status] ?? anuncio.status}
          </span>
          {anuncio.categoria && (
            <span className="rounded-full bg-purple-50 px-2 py-0.5 text-xs font-medium text-purple-700">
              {anuncio.categoria.nome}
            </span>
          )}
        </div>

        <p className="mt-2 truncate text-xs text-gray-500">
          {anuncio.localizacao ? `${anuncio.localizacao}` : 'Localização não informada'}
        </p>
        <p className="mt-1 truncate text-xs text-gray-500">por {anuncio.usuario.nome}</p>
        <p className="mt-1 text-xs text-gray-400">{formatarData(anuncio.criado_em)}</p>
      </div>
    </article>
  );
}

export default function AnunciosPage() {
  const { isAuthenticated } = useAuth();

  const [anuncios, setAnuncios] = useState<Anuncio[]>([]);
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState('');

  const [q, setQ] = useState('');
  const [filtroDoacao, setFiltroDoacao] = useState(false);
  const [filtroTroca, setFiltroTroca] = useState(false);
  const [categoriaId, setCategoriaId] = useState('');
  const [cep, setCep] = useState('');

  const carouselRef = useRef<HTMLDivElement>(null);

  const fetchAnuncios = useCallback(
    async (params: { q?: string; tipo?: string; categoria_id?: string; cep?: string }) => {
      setLoading(true);
      setErrorMessage('');
      try {
        const searchParams = new URLSearchParams();
        if (params.q) searchParams.set('q', params.q);
        if (params.tipo) searchParams.set('tipo', params.tipo);
        if (params.categoria_id) searchParams.set('categoria_id', params.categoria_id);
        if (params.cep) searchParams.set('cep', params.cep);
        searchParams.set('limit', '50');

        const { data } = await api.get<Anuncio[]>(`/anuncios/?${searchParams.toString()}`);
        setAnuncios(data);
      } catch {
        setErrorMessage('Não foi possível carregar os anúncios.');
      } finally {
        setLoading(false);
      }
    },
    [],
  );

  useEffect(() => {
    void fetchAnuncios({});
    api
      .get<Categoria[]>('/categorias/')
      .then(({ data }) => setCategorias(data))
      .catch(() => {});
  }, [fetchAnuncios]);

  function handleSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const ambos = filtroDoacao === filtroTroca;
    const tipo = ambos ? '' : filtroDoacao ? 'doacao' : 'troca';
    void fetchAnuncios({ q: q.trim(), tipo, categoria_id: categoriaId, cep });
  }

  function scrollCarousel(direction: 'left' | 'right') {
    carouselRef.current?.scrollBy({ left: direction === 'left' ? -600 : 600, behavior: 'smooth' });
  }

  return (
    <main className="min-h-screen bg-gray-50 px-4 py-8">
      <div className="mx-auto max-w-6xl space-y-6">
        <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Anúncios</h1>
            <p className="mt-1 text-sm text-gray-500">
              Encontre itens para doação ou troca perto de você.
            </p>
          </div>

          <div className="flex gap-2">
            {isAuthenticated && (
              <Link href="/anuncios/meus">
                <Button variant="outline" type="button">
                  Meus Anúncios
                </Button>
              </Link>
            )}
            {isAuthenticated ? (
              <Link href="/anuncios/novo">
                <Button type="button">
                  <PlusIcon className="mr-2 h-5 w-5" /> Criar Anúncio
                </Button>
              </Link>
            ) : (
              <Link href="/login">
                <Button type="button">Entrar para anunciar</Button>
              </Link>
            )}
          </div>
        </header>

        <section className="rounded-2xl border border-green-300 bg-white p-4 shadow-sm">
          <form
            onSubmit={handleSearch}
            className="flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-end"
          >
            <div className="min-w-[180px] flex-1">
              <label className="mb-1 block text-xs font-medium text-gray-600" htmlFor="q">
                Busca
              </label>
              <input
                id="q"
                type="text"
                value={q}
                onChange={(e) => setQ(e.target.value)}
                placeholder="Título ou descrição..."
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-900 outline-none transition focus:border-green-600 focus:ring-2 focus:ring-green-100"
              />
            </div>

            <div>
              <span className="mb-1 block text-xs font-medium text-gray-600">Tipo</span>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => setFiltroDoacao((v) => !v)}
                  className={`rounded-full border px-3 py-1.5 text-sm font-medium transition-colors ${
                    filtroDoacao
                      ? 'border-green-600 bg-green-600 text-white'
                      : 'border-gray-300 bg-white text-gray-700 hover:border-green-400 hover:text-green-600'
                  }`}
                >
                  Doação
                </button>
                <button
                  type="button"
                  onClick={() => setFiltroTroca((v) => !v)}
                  className={`rounded-full border px-3 py-1.5 text-sm font-medium transition-colors ${
                    filtroTroca
                      ? 'border-blue-600 bg-blue-600 text-white'
                      : 'border-gray-300 bg-white text-gray-700 hover:border-blue-400 hover:text-blue-600'
                  }`}
                >
                  Troca
                </button>
              </div>
            </div>

            {categorias.length > 0 && (
              <div className="w-full sm:w-44">
                <label className="mb-1 block text-xs font-medium text-gray-600" htmlFor="categoria">
                  Categoria
                </label>
                <select
                  id="categoria"
                  value={categoriaId}
                  onChange={(e) => setCategoriaId(e.target.value)}
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-900 outline-none focus:border-green-600 focus:ring-2 focus:ring-green-100"
                >
                  <option value="">Todas</option>
                  {categorias.map((cat) => (
                    <option key={cat.id} value={String(cat.id)}>
                      {cat.nome}
                    </option>
                  ))}
                </select>
              </div>
            )}

            <div className="w-full sm:w-32">
              <label className="mb-1 block text-xs font-medium text-gray-600" htmlFor="cep">
                CEP
              </label>
              <input
                id="cep"
                type="text"
                value={cep}
                onChange={(e) => setCep(formatCepInput(e.target.value))}
                placeholder="00000-000"
                maxLength={9}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-900 outline-none transition focus:border-green-600 focus:ring-2 focus:ring-green-100"
              />
            </div>

            <Button type="submit" isLoading={loading} className="w-full sm:w-auto">
              Buscar
            </Button>
          </form>

          {(filtroDoacao || filtroTroca) && (
            <div className="mt-3 flex flex-wrap items-center gap-2 border-t border-gray-100 pt-3">
              <span className="text-xs text-gray-400">Tipo selecionado:</span>
              {filtroDoacao && (
                <span className="inline-flex items-center gap-1 rounded-full bg-green-100 px-2.5 py-1 text-xs font-bold text-green-700">
                  Doação
                  <button
                    type="button"
                    onClick={() => setFiltroDoacao(false)}
                    aria-label="Remover filtro Doação"
                    className="ml-0.5 hover:text-green-900"
                  >
                    ×
                  </button>
                </span>
              )}
              {filtroTroca && (
                <span className="inline-flex items-center gap-1 rounded-full bg-blue-100 px-2.5 py-1 text-xs font-bold text-blue-700">
                  Troca
                  <button
                    type="button"
                    onClick={() => setFiltroTroca(false)}
                    aria-label="Remover filtro Troca"
                    className="ml-0.5 hover:text-blue-900"
                  >
                    ×
                  </button>
                </span>
              )}
            </div>
          )}
        </section>

        <section>
          {errorMessage ? (
            <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">{errorMessage}</p>
          ) : loading ? (
            <div className="flex items-center justify-center py-16">
              <span className="h-8 w-8 animate-spin rounded-full border-4 border-green-600 border-t-transparent" />
            </div>
          ) : anuncios.length === 0 ? (
            <div className="flex flex-col items-center justify-center rounded-2xl bg-white py-16 shadow-sm">
              <p className="text-gray-500">Nenhum anúncio encontrado.</p>
              {isAuthenticated && (
                <Link href="/anuncios/novo" className="mt-4">
                  <Button type="button">Criar o primeiro anúncio</Button>
                </Link>
              )}
            </div>
          ) : (
            <div className="relative px-6">
              <button
                type="button"
                onClick={() => scrollCarousel('left')}
                aria-label="Rolar para a esquerda"
                className="absolute left-0 top-1/2 z-10 -translate-y-1/2 rounded-full bg-white p-2 shadow-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <svg
                  className="h-5 w-5 text-gray-700"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 19l-7-7 7-7"
                  />
                </svg>
              </button>

              <div
                ref={carouselRef}
                className="flex gap-4 overflow-x-auto pb-4"
                style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
              >
                {anuncios.map((anuncio) => (
                  <Link
                    key={anuncio.id}
                    href={`/anuncios/${anuncio.id}`}
                    className="focus:outline-none"
                  >
                    <AnuncioCard anuncio={anuncio} />
                  </Link>
                ))}
              </div>

              <button
                type="button"
                onClick={() => scrollCarousel('right')}
                aria-label="Rolar para a direita"
                className="absolute right-0 top-1/2 z-10 -translate-y-1/2 rounded-full bg-white p-2 shadow-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <svg
                  className="h-5 w-5 text-gray-700"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5l7 7-7 7"
                  />
                </svg>
              </button>
            </div>
          )}
        </section>

        {!loading && anuncios.length > 0 && (
          <p className="text-center text-xs text-gray-400">
            {anuncios.length} anúncio(s) encontrado(s)
          </p>
        )}
      </div>
    </main>
  );
}
