import DoadoLockerBadge from '@/components/DoadoLockerBadge';
import { API_BASE_URL } from '@/services/api';

function getImageUrl(url: string): string {
  if (!url) return '';
  return url.startsWith('http') ? url : `${API_BASE_URL}${url}`;
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

export interface Anuncio {
  id: number;
  titulo: string;
  tipo: 'doacao' | 'troca' | 'ambos';
  condicao: string;
  status: string;
  localizacao: string | null;
  cep: string | null;
  criado_em: string;
  imagens: AnuncioImagem[];
  categoria: AnuncioCategoria | null;
  usuario: AnuncioUsuario;
  doado_via_locker: boolean;
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

export default function AnuncioCard({ anuncio }: { anuncio: Anuncio }) {
  const primeiraImagem = anuncio.imagens[0]?.url ? getImageUrl(anuncio.imagens[0].url) : null;

  return (
    <article className="group min-w-[272px] max-w-[272px] overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm transition duration-200 hover:-translate-y-0.5 hover:shadow-md">
      <div className="relative h-44 w-full overflow-hidden bg-gray-100">
        {primeiraImagem ? (
          <img src={primeiraImagem} alt={anuncio.titulo} className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-[1.03]" />
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
          {anuncio.doado_via_locker ? (
            <DoadoLockerBadge />
          ) : (
            <span
              className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_COLOR[anuncio.status] ?? 'bg-gray-100 text-gray-600'}`}
            >
              {STATUS_LABEL[anuncio.status] ?? anuncio.status}
            </span>
          )}
          {anuncio.categoria && (
            <span className="rounded-full bg-purple-50 px-2 py-0.5 text-xs font-medium text-purple-700">
              {anuncio.categoria.nome}
            </span>
          )}
        </div>
        <p className="mt-2 truncate text-xs text-gray-500">
          {anuncio.localizacao ?? 'Localização não informada'}
        </p>
        <p className="mt-1 truncate text-xs text-gray-500">por {anuncio.usuario.nome}</p>
        <p className="mt-1 text-xs text-gray-400">{formatarData(anuncio.criado_em)}</p>
      </div>
    </article>
  );
}
