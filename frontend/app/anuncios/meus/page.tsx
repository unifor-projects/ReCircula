'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import Button from '@/components/Button';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/services/api';

interface MeuAnuncio {
  id: number;
  titulo: string;
  tipo: string;
  status: string;
  criado_em: string;
}

interface PerfilResponse {
  id: number;
  nome: string;
  foto_url: string | null;
  localizacao: string | null;
  bio: string | null;
  anuncios_publicados: MeuAnuncio[];
}

function formatarData(dataISO: string): string {
  const data = new Date(dataISO);
  if (Number.isNaN(data.getTime())) return dataISO;
  return new Intl.DateTimeFormat('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' }).format(data);
}

const TIPO_LABEL: Record<string, string> = { doacao: 'Doação', troca: 'Troca', ambos: 'Doação e Troca' };
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
  disponivel: 'bg-emerald-50 text-emerald-700 border border-emerald-200',
  reservado: 'bg-amber-50 text-amber-700 border border-amber-200',
  doado_trocado: 'bg-gray-100 text-gray-500 border border-gray-200',
};

export default function MeusAnunciosPage() {
  const { user, isAuthenticated } = useAuth();
  const router = useRouter();

  const [anuncios, setAnuncios] = useState<MeuAnuncio[]>([]);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState('');
  const [confirmDeleteId, setConfirmDeleteId] = useState<number | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);

  useEffect(() => {
    if (!isAuthenticated || !user) {
      router.replace('/login');
      return;
    }

    async function carregar() {
      setLoading(true);
      setErrorMessage('');
      try {
        const { data } = await api.get<PerfilResponse>(`/usuarios/${user!.id}`);
        setAnuncios(data.anuncios_publicados);
      } catch {
        setErrorMessage('Não foi possível carregar seus anúncios.');
      } finally {
        setLoading(false);
      }
    }

    void carregar();
  }, [isAuthenticated, router, user]);

  async function handleDelete(id: number) {
    setDeletingId(id);
    try {
      await api.delete(`/anuncios/${id}`);
      setAnuncios((prev) => prev.filter((a) => a.id !== id));
      setConfirmDeleteId(null);
    } catch {
      setErrorMessage('Não foi possível excluir o anúncio. Tente novamente.');
    } finally {
      setDeletingId(null);
    }
  }

  if (!isAuthenticated) return null;

  return (
    <main className="min-h-screen bg-gray-50 px-4 py-8">
      <div className="mx-auto max-w-4xl space-y-6">
        <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Meus Anúncios</h1>
            <p className="mt-1 text-sm text-gray-500">Gerencie seus anúncios publicados.</p>
          </div>

          <div className="flex gap-2">
            <Link href="/anuncios">
              <Button variant="outline" type="button">
                ← Todos os Anúncios
              </Button>
            </Link>
            <Link href="/anuncios/novo">
              <Button type="button">+ Criar Anúncio</Button>
            </Link>
          </div>
        </header>

        {errorMessage ? (
          <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">{errorMessage}</p>
        ) : loading ? (
          <div className="flex items-center justify-center py-16">
            <span className="h-8 w-8 animate-spin rounded-full border-4 border-green-600 border-t-transparent" />
          </div>
        ) : anuncios.length === 0 ? (
          <div className="flex flex-col items-center justify-center rounded-2xl bg-white py-16 shadow-sm">
            <p className="text-gray-500">Você ainda não publicou nenhum anúncio.</p>
            <Link href="/anuncios/novo" className="mt-4">
              <Button type="button">Criar meu primeiro anúncio</Button>
            </Link>
          </div>
        ) : (
          <ul className="space-y-3">
            {anuncios.map((anuncio) => (
              <li
                key={anuncio.id}
                className="overflow-hidden rounded-2xl border border-gray-200 bg-white p-4 shadow-sm transition-shadow hover:shadow-md"
              >
                <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                  <div className="flex-1">
                    <h2 className="font-semibold text-gray-900">{anuncio.titulo}</h2>
                    <div className="mt-2 flex flex-wrap gap-1">
                      <span
                        className={`rounded-full px-2 py-0.5 text-xs font-medium ${TIPO_COLOR[anuncio.tipo] ?? 'bg-gray-100 text-gray-600'}`}
                      >
                        {TIPO_LABEL[anuncio.tipo] ?? anuncio.tipo}
                      </span>
                      <span
                        className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_COLOR[anuncio.status] ?? 'bg-gray-100 text-gray-600 border border-gray-200'}`}
                      >
                        {STATUS_LABEL[anuncio.status] ?? anuncio.status}
                      </span>
                    </div>
                    <p className="mt-2 text-xs text-gray-400">Publicado em {formatarData(anuncio.criado_em)}</p>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    <Link href={`/anuncios/${anuncio.id}`}>
                      <Button variant="outline" type="button" className="text-xs">
                        Ver
                      </Button>
                    </Link>
                    <Link href={`/anuncios/${anuncio.id}/editar`}>
                      <Button variant="secondary" type="button" className="text-xs">
                        Editar
                      </Button>
                    </Link>
                    {confirmDeleteId === anuncio.id ? (
                      <>
                        <Button
                          type="button"
                          isLoading={deletingId === anuncio.id}
                          onClick={() => handleDelete(anuncio.id)}
                          className="bg-red-600 text-xs hover:bg-red-700 focus:ring-red-500"
                        >
                          Confirmar
                        </Button>
                        <Button
                          type="button"
                          variant="secondary"
                          className="text-xs"
                          onClick={() => setConfirmDeleteId(null)}
                        >
                          Cancelar
                        </Button>
                      </>
                    ) : (
                      <button
                        type="button"
                        onClick={() => setConfirmDeleteId(anuncio.id)}
                        className="rounded-lg border border-red-200 px-3 py-1.5 text-xs font-medium text-red-600 transition hover:bg-red-50"
                      >
                        Excluir
                      </button>
                    )}
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}

        {!loading && anuncios.length > 0 && (
          <p className="text-center text-xs text-gray-400">{anuncios.length} anúncio(s) publicado(s)</p>
        )}
      </div>
    </main>
  );
}
