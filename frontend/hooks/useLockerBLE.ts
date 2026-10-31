'use client';

import { useCallback, useRef, useState } from 'react';

/**
 * UUIDs do serviço BLE do ESP32.
 * O firmware do ESP32 deve anunciar o mesmo SERVICE_UUID e expor uma
 * característica gravável com CHARACTERISTIC_UUID.
 *
 * Comandos:
 *   0x01 → abrir (destrancar a trava)
 *   0x00 → fechar (trancar a trava)
 */
export const LOCKER_SERVICE_UUID = '4fafc201-1fb5-459e-8fcc-c5c9c331914b';
export const LOCKER_CHAR_UUID = 'beb5483e-36e1-4688-b7f5-ea07361b26a8';

const CMD_ABRIR = 0x01;
const CMD_FECHAR = 0x00;

export type BLEStatus = 'desconectado' | 'conectando' | 'conectado' | 'erro';

export interface BLELogEntry {
  id: number;
  timestamp: Date;
  message: string;
  type: 'info' | 'success' | 'error';
}

let logCounter = 0;

export function useLockerBLE() {
  const [status, setStatus] = useState<BLEStatus>('desconectado');
  const [deviceName, setDeviceName] = useState<string | null>(null);
  const [log, setLog] = useState<BLELogEntry[]>([]);
  const [isSending, setIsSending] = useState(false);

  const deviceRef = useRef<BluetoothDevice | null>(null);
  const charRef = useRef<BluetoothRemoteGATTCharacteristic | null>(null);

  const addLog = useCallback((message: string, type: BLELogEntry['type'] = 'info') => {
    setLog((prev) =>
      [{ id: ++logCounter, timestamp: new Date(), message, type }, ...prev].slice(0, 30),
    );
  }, []);

  const conectar = useCallback(async () => {
    if (!navigator.bluetooth) {
      addLog(
        'Web Bluetooth não é suportado neste navegador. Use Chrome ou Edge em desktop.',
        'error',
      );
      setStatus('erro');
      return;
    }

    setStatus('conectando');
    addLog('Procurando dispositivos BLE próximos...');

    try {
      const device = await navigator.bluetooth.requestDevice({
        filters: [{ services: [LOCKER_SERVICE_UUID] }],
      });

      device.addEventListener('gattserverdisconnected', () => {
        setStatus('desconectado');
        setDeviceName(null);
        charRef.current = null;
        addLog('Dispositivo desconectado.', 'error');
      });

      const nome = device.name ?? 'ReCircula Locker';
      addLog(`Conectando ao dispositivo "${nome}"...`);

      const server = await device.gatt!.connect();
      const service = await server.getPrimaryService(LOCKER_SERVICE_UUID);
      const characteristic = await service.getCharacteristic(LOCKER_CHAR_UUID);

      deviceRef.current = device;
      charRef.current = characteristic;

      setDeviceName(nome);
      setStatus('conectado');
      addLog(`Conectado ao locker "${nome}".`, 'success');
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Erro desconhecido';
      // O usuário fechou o seletor de dispositivos — não é um erro real
      if (
        msg.toLowerCase().includes('user cancelled') ||
        msg.toLowerCase().includes('cancelled') ||
        msg.toLowerCase().includes('user denied')
      ) {
        setStatus('desconectado');
        addLog('Seleção de dispositivo cancelada.');
        return;
      }
      setStatus('erro');
      addLog(`Falha na conexão: ${msg}`, 'error');
    }
  }, [addLog]);

  const desconectar = useCallback(() => {
    deviceRef.current?.gatt?.disconnect();
    deviceRef.current = null;
    charRef.current = null;
    setStatus('desconectado');
    setDeviceName(null);
    addLog('Desconectado.');
  }, [addLog]);

  /**
   * Envia um comando BLE ao ESP32.
   * Retorna `true` se o envio foi bem-sucedido.
   */
  const enviarComando = useCallback(
    async (comando: 'abrir' | 'fechar'): Promise<boolean> => {
      if (!charRef.current) {
        addLog('Nenhum dispositivo conectado.', 'error');
        return false;
      }

      setIsSending(true);
      try {
        const byte = comando === 'abrir' ? CMD_ABRIR : CMD_FECHAR;
        await charRef.current.writeValue(new Uint8Array([byte]));
        const label = comando === 'abrir' ? 'Abrir' : 'Fechar';
        addLog(`Comando "${label}" enviado com sucesso.`, 'success');
        return true;
      } catch (err) {
        const msg = err instanceof Error ? err.message : 'Erro desconhecido';
        addLog(`Falha ao enviar comando: ${msg}`, 'error');
        return false;
      } finally {
        setIsSending(false);
      }
    },
    [addLog],
  );

  const isBLESupported = typeof navigator !== 'undefined' && !!navigator.bluetooth;

  return {
    status,
    deviceName,
    log,
    isSending,
    isBLESupported,
    conectar,
    desconectar,
    enviarComando,
  };
}
