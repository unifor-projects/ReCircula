import { ArrowLeft, HeartHandshake, MapPin, Recycle } from 'lucide-react';
import Image from 'next/image';
import Link from 'next/link';
import type { ReactNode } from 'react';

const DESTAQUES = [
  { icon: Recycle, texto: 'Dê uma segunda vida ao que ainda funciona' },
  { icon: MapPin, texto: 'Encontre itens perto de você' },
  { icon: HeartHandshake, texto: 'Doações gratuitas para quem precisa' },
];

export default function AuthShell({ title, subtitle, children }: { title: string; subtitle: string; children: ReactNode }) {
  return (
    <main className='grid min-h-screen bg-gray-50 lg:grid-cols-2'>
      {/* Painel da marca (desktop) */}
      <aside className='relative hidden overflow-hidden bg-gray-900 p-12 text-white lg:flex lg:flex-col lg:justify-between'>
        {/* Foto do locker ao fundo, escurecida para o texto ler bem */}
        <Image src='/locker.jpeg' alt='' fill sizes='50vw' className='object-cover object-[50%_55%] opacity-40' />
        <div className='pointer-events-none absolute inset-0 bg-gradient-to-t from-gray-900 via-gray-900/80 to-gray-900/40' />

        <Link href='/' translate='no' className='relative font-mono text-2xl font-extrabold tracking-tight text-lime-300'>
          ReCircula
        </Link>

        <div className='relative'>
          <p className='text-balance text-4xl font-extrabold leading-tight'>
            O que não serve mais para você pode mudar o dia de alguém.
          </p>
          <ul className='mt-8 space-y-4'>
            {DESTAQUES.map(({ icon: Icon, texto }) => (
              <li key={texto} className='flex items-center gap-3 text-gray-100'>
                <span className='flex h-9 w-9 items-center justify-center rounded-lg bg-lime-300 text-gray-900'>
                  <Icon size={18} aria-hidden='true' />
                </span>
                {texto}
              </li>
            ))}
          </ul>
        </div>

        <p className='relative text-sm text-gray-400'>Economia circular ao alcance de todos.</p>
      </aside>

      {/* Formulário */}
      <section className='flex flex-col px-4 py-8 sm:px-8'>
        <Link href='/' className='inline-flex w-fit items-center gap-1 text-sm text-gray-500 transition hover:text-green-700'>
          <ArrowLeft size={16} aria-hidden='true' /> Voltar para o início
        </Link>

        <div className='mx-auto flex w-full max-w-md flex-1 flex-col justify-center py-8'>
          <div className='animate-enter rounded-3xl bg-white p-6 shadow-xl shadow-gray-200/60 ring-1 ring-gray-100 sm:p-8'>
            <p translate='no' className='font-mono text-xl font-extrabold text-green-600 lg:hidden'>ReCircula</p>
            <h1 className='mt-2 text-3xl font-bold text-gray-900 lg:mt-0'>{title}</h1>
            <p className='mt-2 text-gray-600'>{subtitle}</p>
            <div className='mt-8'>{children}</div>
          </div>
        </div>
      </section>
    </main>
  );
}
