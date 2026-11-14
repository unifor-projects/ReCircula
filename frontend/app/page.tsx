import {
  Armchair,
  Check,
  Lock,
  MapPin,
  MessageCircle,
  PackageCheck,
  Recycle,
  ShieldCheck,
  Wifi,
} from 'lucide-react';
import Image from 'next/image';
import Link from 'next/link';
import DoadoLockerBadge from '@/components/DoadoLockerBadge';
import HeroAcoes from '@/components/home/HeroAcoes';
import ItensRecentes from '@/components/home/ItensRecentes';

// Números do Relatório Científico (Fundamentação Teórica, seção 2.1)
const DADOS = [
  {
    valor: '91%',
    texto: 'do impacto ambiental de um utilitário plástico acontece na fabricação, não no descarte.',
    fonte: 'Mannheim; Simenfalvi, 2020',
  },
  {
    valor: 'até 43%',
    texto: 'do lixo plástico do mundo termina em aterros sanitários e lixões.',
    fonte: 'Mannheim; Simenfalvi, 2020',
  },
  {
    valor: '+2,5\u00a0mi\u00a0t',
    texto: 'de eletroeletrônicos entram no fluxo global a cada ano, muitos ainda funcionando.',
    fonte: 'Dias et al., 2024',
  },
];

const PASSOS = [
  { icon: Recycle, titulo: 'Anuncie', texto: 'Publique com fotos aquele item que ainda funciona e você não usa mais.' },
  { icon: MapPin, titulo: 'Encontre perto', texto: 'Busque por categoria e pela distância até o seu CEP.' },
  { icon: MessageCircle, titulo: 'Combine', texto: 'Converse pelo chat interno, sem expor telefone ou endereço.' },
  { icon: PackageCheck, titulo: 'Entregue', texto: 'Entregue em mãos ou deixe o item em um locker ReCircula.' },
];

const GARANTIAS = ['100% gratuito', 'Busca por proximidade', 'Chat sem expor seu telefone'];

const LOCKER_PASSOS = [
  'Toque em “Abrir locker” no anúncio, de qualquer celular',
  'Guarde o item e feche a porta',
  'Confirme no app: o anúncio vira “Doado no locker”',
];

export default function Home() {
  return (
    <main className='bg-white text-gray-900'>
      {/* Hero: texto à esquerda, o fluxo do app à direita */}
      <section className='relative overflow-hidden bg-gradient-to-b from-lime-50 via-white to-white'>
        <div className='pointer-events-none absolute -right-24 -top-24 h-96 w-96 rounded-full bg-lime-200/50 blur-3xl' />

        <div className='relative mx-auto grid max-w-5xl items-center gap-12 px-4 py-16 lg:grid-cols-[1.15fr_1fr] lg:py-24'>
          <div className='flex flex-col items-center text-center lg:items-start lg:text-left'>
            <p
              translate='no'
              className='animate-enter rounded-full bg-lime-100 px-4 py-1 font-mono text-sm font-semibold text-green-800'
            >
              ReCircula
            </p>
            <h1 className='animate-enter mt-6 text-balance text-4xl font-extrabold tracking-tight [animation-delay:80ms] sm:text-5xl lg:text-6xl'>
              Doe e troque <span className='text-green-600'>o que ainda funciona</span>
            </h1>
            <p className='animate-enter mt-5 max-w-xl text-pretty text-lg text-gray-600 [animation-delay:160ms]'>
              O que não serve mais para você pode mudar o dia de alguém. Anuncie de graça, encontre itens perto de casa
              e faça os objetos circularem.
            </p>

            <div className='animate-enter w-full [animation-delay:240ms] sm:w-auto'>
              <HeroAcoes />
            </div>

            <ul className='animate-enter mt-8 flex flex-wrap justify-center gap-x-6 gap-y-2 text-sm text-gray-600 [animation-delay:320ms] lg:justify-start'>
              {GARANTIAS.map((g) => (
                <li key={g} className='flex items-center gap-1.5'>
                  <Check size={16} aria-hidden='true' className='text-green-600' />
                  {g}
                </li>
              ))}
            </ul>
          </div>

          {/* Recortes da interface contando o fluxo: anúncio, conversa, doação no locker */}
          <div className='animate-enter relative mx-auto w-full max-w-sm [animation-delay:200ms]' aria-hidden='true'>
            <div className='rounded-2xl bg-white p-4 shadow-xl ring-1 ring-gray-100'>
              <div className='flex items-center gap-3'>
                <span className='flex h-12 w-12 items-center justify-center rounded-xl bg-lime-100 text-green-700'>
                  <Armchair size={24} />
                </span>
                <div className='min-w-0'>
                  <p className='truncate font-semibold'>Cadeira infantil</p>
                  <p className='text-sm text-gray-500'>Usado · a 2 km de você</p>
                </div>
                <span className='ml-auto rounded-full bg-green-100 px-2 py-0.5 text-xs font-bold text-green-700'>Doação</span>
              </div>
            </div>

            <div className='ml-8 mt-4 space-y-2 rounded-2xl bg-white p-4 shadow-xl ring-1 ring-gray-100'>
              <p className='w-fit rounded-2xl rounded-bl-sm bg-gray-100 px-3 py-2 text-sm'>Oi! Ainda está disponível?</p>
              <p className='ml-auto w-fit rounded-2xl rounded-br-sm bg-green-600 px-3 py-2 text-sm text-white'>
                Sim! Deixo no locker amanhã.
              </p>
            </div>

            <div className='mt-4 flex items-center justify-between rounded-2xl bg-gray-900 p-4 text-white shadow-xl'>
              <span className='flex items-center gap-2 text-sm font-semibold'>
                <Lock size={16} className='text-lime-300' /> Locker UNI01
              </span>
              <DoadoLockerBadge />
            </div>
          </div>
        </div>
      </section>

      {/* Produto real: anúncios do banco */}
      <ItensRecentes />

      {/* Problema */}
      <section className='bg-gray-50'>
        <div className='mx-auto max-w-5xl px-4 py-16'>
          <p className='text-sm font-semibold uppercase tracking-wider text-green-600'>Por que existimos</p>
          <h2 className='mt-2 max-w-3xl text-2xl font-bold sm:text-3xl'>
            Jogar fora um item que funciona sai caro para o planeta
          </h2>
          <p className='mt-3 max-w-3xl text-gray-600'>
            Fast fashion, obsolescência programada e o ciclo <em>extrair, produzir, consumir e descartar</em> lotam os
            aterros e exigem cada vez mais matéria-prima. A saída mais eficiente é simples: fazer o que já existe durar
            mais.
          </p>

          <div className='mt-8 grid gap-4 sm:grid-cols-3'>
            {DADOS.map((d) => (
              <div key={d.valor} className='rounded-2xl border border-gray-100 bg-white p-6 shadow-sm'>
                <p className='font-mono text-4xl font-extrabold text-green-700'>{d.valor}</p>
                <p className='mt-3 text-sm text-gray-700'>{d.texto}</p>
                <p className='mt-4 text-xs text-gray-500'>{d.fonte}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Como funciona */}
      <section className='mx-auto max-w-5xl px-4 py-16'>
        <p className='text-sm font-semibold uppercase tracking-wider text-green-600'>Como funciona</p>
        <h2 className='mt-2 text-2xl font-bold sm:text-3xl'>Do armário para outras mãos em 4 passos</h2>

        <ol className='mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4'>
          {PASSOS.map(({ icon: Icon, titulo, texto }) => (
            <li
              key={titulo}
              className='rounded-2xl bg-white p-5 shadow-sm ring-1 ring-gray-100 transition duration-200 hover:-translate-y-0.5 hover:shadow-md'
            >
              <span className='flex h-10 w-10 items-center justify-center rounded-xl bg-green-600 text-white'>
                <Icon size={20} aria-hidden='true' />
              </span>
              <h3 className='mt-4 font-semibold'>{titulo}</h3>
              <p className='mt-1 text-sm text-gray-600'>{texto}</p>
            </li>
          ))}
        </ol>
      </section>

      {/* Locker */}
      <section className='bg-gray-900 text-white'>
        <div className='mx-auto grid max-w-5xl items-center gap-10 px-4 py-16 md:grid-cols-2'>
          <div>
            <p className='text-sm font-semibold uppercase tracking-wider text-lime-300'>Locker ReCircula</p>
            <h2 className='mt-2 text-2xl font-bold sm:text-3xl'>Doe sem precisar marcar horário</h2>
            <p className='mt-3 text-gray-300'>
              Sem tempo para encontrar quem vai receber? Deixe o item em um locker. O registro fica salvo no anúncio.
            </p>
            <ol className='mt-6 space-y-3'>
              {LOCKER_PASSOS.map((passo, i) => (
                <li key={passo} className='flex items-start gap-3'>
                  <span className='flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-lime-300 text-sm font-bold text-gray-900'>
                    {i + 1}
                  </span>
                  <span className='pt-0.5 text-gray-100'>{passo}</span>
                </li>
              ))}
            </ol>
          </div>

          {/* Foto do protótipo + recorte do controle do locker */}
          <div className='relative mx-auto w-full max-w-sm pb-10'>
            <div className='group relative aspect-[4/5] overflow-hidden rounded-3xl shadow-2xl ring-8 ring-white/10'>
              <Image
                src='/locker.jpeg'
                alt='Locker ReCircula: caixa verde com a marca ReCircula na porta'
                fill
                sizes='(min-width: 768px) 384px, 100vw'
                className='object-cover object-[50%_55%] transition-transform duration-500 group-hover:scale-[1.03]'
              />
            </div>

            <div className='absolute -bottom-2 left-4 right-4 rounded-2xl bg-white p-4 text-gray-900 shadow-xl sm:-left-8 sm:right-auto sm:w-64'>
              <div className='flex items-center justify-between gap-2'>
                <span className='flex items-center gap-2 whitespace-nowrap text-sm font-semibold'>
                  <Wifi size={16} className='text-green-600' aria-hidden='true' /> Locker UNI01
                </span>
                <span className='flex items-center gap-1.5 rounded-full bg-green-50 px-2 py-0.5 text-xs font-medium text-green-700'>
                  <span className='h-2 w-2 rounded-full bg-green-500 motion-safe:animate-pulse' /> Conectado
                </span>
              </div>
              <div className='mt-3 grid grid-cols-2 gap-2' aria-hidden='true'>
                <span className='rounded-lg bg-green-600 py-2 text-center text-sm font-semibold text-white'>Abrir</span>
                <span className='rounded-lg border border-gray-300 py-2 text-center text-sm font-semibold text-gray-700'>Fechar</span>
              </div>
              <p className='mt-3 flex items-center gap-1.5 text-xs text-gray-500'>
                <ShieldCheck size={14} aria-hidden='true' /> Aberturas ficam registradas no anúncio
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA final */}
      <section className='px-4 py-16'>
        <div className='mx-auto max-w-5xl rounded-3xl border border-lime-100 bg-lime-50 px-6 py-12 text-center'>
          <h2 className='text-2xl font-bold sm:text-3xl'>Dê uma segunda vida ao que você tem em casa</h2>
          <p className='mt-2 text-gray-600'>É gratuito, evita descarte e leva o item a quem precisa.</p>
          <Link
            href='/anuncios/novo'
            className='mt-6 inline-block rounded-xl bg-green-600 px-6 py-3 font-semibold text-white shadow transition hover:-translate-y-0.5 hover:bg-green-700 active:scale-[0.98]'
          >
            Anunciar um item
          </Link>
        </div>
      </section>

      <footer className='border-t border-gray-100 py-6 text-center text-xs text-gray-500'>
        ReCircula · Projeto acadêmico de Ciência da Computação, Unifor · 2026
      </footer>
    </main>
  );
}
