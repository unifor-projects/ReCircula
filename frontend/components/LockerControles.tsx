'use client';

import { AxiosError } from 'axios';
import { Lock, LockOpen } from 'lucide-react';
import Link from 'next/link';
import { useState } from 'react';
import { loginUrl, useAuth } from '@/contexts/AuthContext';
import api from '@/services/api';

// Caminho Wi-Fi desativado: o controle do locker é feito via Bluetooth (BLE).
// Para reativar, mude para true.
const WIFI_ENABLED = false;

/** Abre/fecha o locker pelo backend; o ESP32 recebe o comando pelo Wi-Fi. */
export default function LockerControles({ anuncioId }: { anuncioId: number }) {
  if (!WIFI_ENABLED) return null;
  const { isAuthenticated } = useAuth();
  const [enviando, setEnviando] = useState<'abrir' | 'fechar' | null>(null);
  const [retorno, setRetorno] = useState<{ ok: boolean; msg: string } | null>(null);

  if (!isAuthenticated) {
    return (
      <Link
        href={loginUrl(`/anuncios/${anuncioId}`)}
        className='flex w-full items-center justify-center gap-2 rounded-lg border border-green-300 px-4 py-2.5 text-sm font-medium text-green-700 transition hover:bg-green-50'
      >
        <LockOpen size={16} aria-hidden='true' />
        Entre para abrir o locker
      </Link>
    );
  }

  async function acionar(acao: 'abrir' | 'fechar') {
    setEnviando(acao);
    setRetorno(null);
    try {
      await api.post(`/anuncios/${anuncioId}/locker/${acao}`);
      setRetorno({
        ok: true,
        msg: acao === 'abrir' ? 'Comando enviado: o locker abre em instantes.' : 'Comando enviado: o locker fecha em instantes.',
      });
    } catch (error) {
      const detail = error instanceof AxiosError ? (error.response?.data as { detail?: string } | undefined)?.detail : undefined;
      setRetorno({ ok: false, msg: detail ?? 'Não foi possível falar com o locker. Tente de novo.' });
    } finally {
      setEnviando(null);
    }
  }

  const botao =
    'flex items-center justify-center gap-2 rounded-lg px-4 py-2.5 text-sm font-medium transition disabled:opacity-60';

  return (
    <div className='space-y-2'>
      <div className='grid grid-cols-2 gap-2'>
        <button
          type='button'
          onClick={() => void acionar('abrir')}
          disabled={enviando !== null}
          className={`${botao} bg-green-600 text-white hover:bg-green-700`}
        >
          <LockOpen size={16} aria-hidden='true' />
          {enviando === 'abrir' ? 'Abrindo…' : 'Abrir locker'}
        </button>
        <button
          type='button'
          onClick={() => void acionar('fechar')}
          disabled={enviando !== null}
          className={`${botao} border border-gray-300 text-gray-700 hover:bg-gray-50`}
        >
          <Lock size={16} aria-hidden='true' />
          {enviando === 'fechar' ? 'Fechando…' : 'Fechar locker'}
        </button>
      </div>
      <p aria-live='polite' className={`text-xs ${retorno?.ok ? 'text-green-700' : 'text-red-600'}`}>
        {retorno?.msg}
      </p>
    </div>
  );
}
