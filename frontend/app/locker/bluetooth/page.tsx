'use client';

import { Bluetooth, BluetoothConnected, BluetoothOff, LockOpen, Lock, Unplug, AlertTriangle } from 'lucide-react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { Suspense } from 'react';
import { useLockerBLE } from '@/hooks/useLockerBLE';
import api from '@/services/api';

// ─── Status indicator ───────────────────────────────────────────────────────

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, { label: string; dot: string; text: string }> = {
    desconectado: { label: 'Desconectado', dot: 'bg-gray-400', text: 'text-gray-600' },
    conectando: { label: 'Conectando…', dot: 'bg-amber-400 animate-pulse', text: 'text-amber-700' },
    conectado: { label: 'Conectado', dot: 'bg-green-500', text: 'text-green-700' },
    erro: { label: 'Erro', dot: 'bg-red-500', text: 'text-red-700' },
  };
  const cfg = map[status] ?? map.desconectado;
  return (
    <span className={`flex items-center gap-1.5 text-sm font-medium ${cfg.text}`}>
      <span className={`h-2 w-2 rounded-full ${cfg.dot}`} />
      {cfg.label}
    </span>
  );
}

// ─── Log entry ───────────────────────────────────────────────────────────────

function LogLine({ entry }: { entry: { id: number; timestamp: Date; message: string; type: string } }) {
  const colorMap: Record<string, string> = {
    info: 'text-gray-500',
    success: 'text-green-600',
    error: 'text-red-600',
  };
  const time = entry.timestamp.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  return (
    <li className={`flex gap-2 text-xs ${colorMap[entry.type] ?? 'text-gray-500'}`}>
      <span className="w-20 shrink-0 font-mono text-gray-400">{time}</span>
      <span>{entry.message}</span>
    </li>
  );
}

// ─── Main inner component (uses useSearchParams) ─────────────────────────────

function BLEControlInner() {
  const searchParams = useSearchParams();
  const anuncioId = searchParams?.get('anuncioId') ?? null;

  const {
    status,
    deviceName,
    log,
    isSending,
    isBLESupported,
    conectar,
    desconectar,
    enviarComando,
  } = useLockerBLE();

  const isConnected = status === 'conectado';

  /**
   * Envia o comando BLE e, se `anuncioId` foi passado via query param,
   * registra a ação na API do backend para auditoria.
   */
  async function handleAction(acao: 'abrir' | 'fechar') {
    const ok = await enviarComando(acao);
    if (!ok || !anuncioId) return;
    try {
      await api.post(`/anuncios/${anuncioId}/locker/${acao}`);
    } catch {
      // O registro na API é auxiliar — falha silenciosa para não bloquear o fluxo BLE
    }
  }

  return (
    <main className="min-h-screen bg-gray-50 px-4 py-8">
      <div className="mx-auto max-w-lg space-y-5">
        {/* Breadcrumb */}
        <nav className="flex items-center gap-2 text-sm text-gray-500">
          <Link href="/anuncios" className="hover:text-green-600">
            Anúncios
          </Link>
          <span>/</span>
          <span className="text-gray-900">Controle Bluetooth do Locker</span>
        </nav>

        {/* Header */}
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-green-100">
            <Bluetooth size={20} className="text-green-700" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-gray-900">Controle Bluetooth</h1>
            <p className="text-xs text-gray-500">Abrir ou fechar o locker via BLE (ESP32)</p>
          </div>
        </div>

        {/* Aviso: browser sem suporte */}
        {!isBLESupported && (
          <div className="flex items-start gap-3 rounded-xl border border-amber-200 bg-amber-50 p-4">
            <AlertTriangle size={18} className="mt-0.5 shrink-0 text-amber-600" />
            <div className="text-sm">
              <p className="font-semibold text-amber-800">Navegador não suportado</p>
              <p className="mt-0.5 text-amber-700">
                A Web Bluetooth API requer <strong>Chrome</strong> ou <strong>Edge</strong> em
                desktop. Outros navegadores (Firefox, Safari) não têm suporte.
              </p>
            </div>
          </div>
        )}

        {/* Card de conexão */}
        <div className="rounded-2xl bg-white p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">Dispositivo</p>
              {deviceName ? (
                <p className="mt-0.5 font-medium text-gray-900">{deviceName}</p>
              ) : (
                <p className="mt-0.5 text-sm text-gray-400">Nenhum dispositivo conectado</p>
              )}
            </div>
            <StatusBadge status={status} />
          </div>

          <div className="mt-4 flex gap-2">
            {!isConnected ? (
              <button
                type="button"
                onClick={() => void conectar()}
                disabled={!isBLESupported || status === 'conectando'}
                className="flex flex-1 items-center justify-center gap-2 rounded-lg bg-green-600 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-green-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {status === 'conectando' ? (
                  <>
                    <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                    Conectando…
                  </>
                ) : (
                  <>
                    <BluetoothConnected size={16} />
                    Conectar ao locker
                  </>
                )}
              </button>
            ) : (
              <button
                type="button"
                onClick={desconectar}
                className="flex items-center gap-2 rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-medium text-gray-700 transition hover:bg-gray-50"
              >
                <Unplug size={16} />
                Desconectar
              </button>
            )}
          </div>
        </div>

        {/* Botões de controle */}
        <div className="rounded-2xl bg-white p-5 shadow-sm">
          <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-gray-500">
            Controlar trava
          </p>

          <div className="grid grid-cols-2 gap-3">
            {/* Abrir */}
            <button
              type="button"
              onClick={() => void handleAction('abrir')}
              disabled={!isConnected || isSending}
              className="flex flex-col items-center gap-2 rounded-xl border-2 border-green-200 bg-green-50 px-4 py-5 text-green-700 transition hover:border-green-400 hover:bg-green-100 disabled:cursor-not-allowed disabled:opacity-40"
            >
              {isSending ? (
                <span className="h-7 w-7 animate-spin rounded-full border-2 border-green-600 border-t-transparent" />
              ) : (
                <LockOpen size={28} />
              )}
              <span className="text-sm font-semibold">Abrir</span>
              <span className="text-center text-xs text-green-600">Destrancar a trava</span>
            </button>

            {/* Fechar */}
            <button
              type="button"
              onClick={() => void handleAction('fechar')}
              disabled={!isConnected || isSending}
              className="flex flex-col items-center gap-2 rounded-xl border-2 border-gray-200 bg-gray-50 px-4 py-5 text-gray-700 transition hover:border-gray-400 hover:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-40"
            >
              {isSending ? (
                <span className="h-7 w-7 animate-spin rounded-full border-2 border-gray-600 border-t-transparent" />
              ) : (
                <Lock size={28} />
              )}
              <span className="text-sm font-semibold">Fechar</span>
              <span className="text-center text-xs text-gray-500">Trancar a trava</span>
            </button>
          </div>

          {!isConnected && (
            <p className="mt-3 text-center text-xs text-gray-400">
              Conecte ao locker para habilitar os controles.
            </p>
          )}
        </div>

        {/* Log de atividade */}
        <div className="rounded-2xl bg-white p-5 shadow-sm">
          <div className="mb-3 flex items-center justify-between">
            <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">
              Log de atividade
            </p>
            {log.length === 0 && (
              <BluetoothOff size={14} className="text-gray-300" />
            )}
          </div>

          {log.length === 0 ? (
            <p className="text-center text-xs text-gray-400 py-4">Nenhuma atividade ainda.</p>
          ) : (
            <ul className="space-y-1.5">
              {log.map((entry) => (
                <LogLine key={entry.id} entry={entry} />
              ))}
            </ul>
          )}
        </div>
      </div>
    </main>
  );
}

// ─── Page wrapper (Suspense required for useSearchParams in Next.js 15) ───────

export default function BLELockerPage() {
  return (
    <Suspense>
      <BLEControlInner />
    </Suspense>
  );
}
