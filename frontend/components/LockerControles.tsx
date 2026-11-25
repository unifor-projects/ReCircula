'use client';

import { AxiosError } from 'axios';
import { AlertTriangle, Bluetooth, BluetoothConnected, Lock, LockOpen, Unplug } from 'lucide-react';
import Link from 'next/link';
import { useState } from 'react';
import { useLockerBLE } from '@/hooks/useLockerBLE';
import { loginUrl, useAuth } from '@/contexts/AuthContext';
import api from '@/services/api';

// Caminho Wi-Fi desativado: o controle do locker é feito via Bluetooth (BLE).
// Para reativar, mude para true.
const WIFI_ENABLED = false;

// ─── Controles BLE inline ────────────────────────────────────────────────────

function LockerControlesBLE({ anuncioId }: { anuncioId: number }) {
  const { status, deviceName, isSending, isBLESupported, conectar, desconectar, enviarComando } = useLockerBLE();
  const isConnected = status === 'conectado';

  async function handleAction(acao: 'abrir' | 'fechar') {
    const ok = await enviarComando(acao);
    if (!ok) return;
    try {
      await api.post(`/anuncios/${anuncioId}/locker/${acao}`);
    } catch {
      // registro auxiliar — falha silenciosa
    }
  }

  if (!isBLESupported) {
    return (
      <div className="flex items-start gap-2 rounded-lg border border-amber-200 bg-amber-50 p-3 text-xs text-amber-700">
        <AlertTriangle size={14} className="mt-0.5 shrink-0" />
        <span>
          Web Bluetooth requer <strong>Chrome</strong> ou <strong>Edge</strong> em desktop/Android, e conexão{' '}
          <strong>HTTPS</strong> ou <strong>localhost</strong>.
        </span>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {/* Status + botão conectar/desconectar */}
      {!isConnected ? (
        <button
          type="button"
          onClick={() => void conectar()}
          disabled={status === 'conectando'}
          className="flex w-full items-center justify-center gap-2 rounded-lg bg-green-600 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-green-700 disabled:opacity-60"
        >
          {status === 'conectando' ? (
            <>
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
              Conectando…
            </>
          ) : (
            <>
              <BluetoothConnected size={16} />
              Conectar ao locker via Bluetooth
            </>
          )}
        </button>
      ) : (
        <>
          <div className="flex items-center justify-between rounded-lg border border-green-200 bg-green-50 px-3 py-2">
            <div className="flex items-center gap-2 text-sm text-green-800">
              <Bluetooth size={14} />
              <span className="font-medium">{deviceName ?? 'Locker conectado'}</span>
            </div>
            <button
              type="button"
              onClick={desconectar}
              className="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-700"
            >
              <Unplug size={12} />
              Desconectar
            </button>
          </div>

          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => void handleAction('abrir')}
              disabled={isSending}
              className="flex items-center justify-center gap-2 rounded-lg bg-green-600 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-green-700 disabled:opacity-60"
            >
              {isSending ? (
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
              ) : (
                <LockOpen size={16} />
              )}
              Abrir locker
            </button>
            <button
              type="button"
              onClick={() => void handleAction('fechar')}
              disabled={isSending}
              className="flex items-center justify-center gap-2 rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-medium text-gray-700 transition hover:bg-gray-50 disabled:opacity-60"
            >
              {isSending ? (
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-gray-500 border-t-transparent" />
              ) : (
                <Lock size={16} />
              )}
              Fechar locker
            </button>
          </div>
        </>
      )}
    </div>
  );
}

// ─── Controles Wi-Fi inline ──────────────────────────────────────────────────

function LockerControlesWifi({ anuncioId }: { anuncioId: number }) {
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

// ─── Componente principal ────────────────────────────────────────────────────

/** Abre/fecha o locker; quando Wi-Fi desativado usa BLE inline. */
export default function LockerControles({ anuncioId }: { anuncioId: number }) {
  if (!WIFI_ENABLED) return <LockerControlesBLE anuncioId={anuncioId} />;
  return <LockerControlesWifi anuncioId={anuncioId} />;
}
