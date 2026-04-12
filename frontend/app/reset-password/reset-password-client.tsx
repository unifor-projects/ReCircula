'use client';

import { AxiosError } from 'axios';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { FormEvent, useMemo, useState } from 'react';
import Button from '@/components/Button';
import { authClient } from '@/services/authClient';

interface ResetPasswordResponse {
  detail: string;
}

const MIN_PASSWORD_LENGTH = 6;

export default function ResetPasswordClient() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams?.get('token') ?? null;
  const [novaSenha, setNovaSenha] = useState('');
  const [confirmacaoSenha, setConfirmacaoSenha] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const validationMessage = useMemo(() => {
    if (!token) return 'O link de redefinição está incompleto.';
    if (novaSenha.length < MIN_PASSWORD_LENGTH) return `A nova senha deve ter pelo menos ${MIN_PASSWORD_LENGTH} caracteres.`;
    if (novaSenha !== confirmacaoSenha) return 'A confirmação de senha não confere.';
    return '';
  }, [confirmacaoSenha, novaSenha, token]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErrorMessage('');
    setSuccessMessage('');

    if (validationMessage) {
      setErrorMessage(validationMessage);
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await authClient.post<ResetPasswordResponse>('/auth/reset-password', {
        token,
        nova_senha: novaSenha,
      });
      setSuccessMessage(response.data?.detail ?? 'Senha redefinida com sucesso.');
      setNovaSenha('');
      setConfirmacaoSenha('');
      window.setTimeout(() => {
        router.push('/login');
      }, 1800);
    } catch (error) {
      const detail = error instanceof AxiosError ? (error.response?.data as { detail?: string } | undefined)?.detail : undefined;
      setErrorMessage(detail ?? 'Não foi possível redefinir sua senha.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className='relative flex min-h-screen items-center justify-center overflow-hidden bg-[radial-gradient(circle_at_top,_rgba(22,163,74,0.18),_transparent_36%),linear-gradient(135deg,_#f8fafc_0%,_#eef7ee_100%)] px-4 py-8 text-gray-900'>
      <div className='absolute inset-x-0 top-0 h-40 bg-gradient-to-b from-green-100/50 to-transparent' />
      <section className='relative w-full max-w-lg rounded-3xl border border-white/70 bg-white/90 p-6 shadow-[0_20px_70px_rgba(15,23,42,0.12)] backdrop-blur sm:p-8'>
        <p className='text-xs font-semibold uppercase tracking-[0.2em] text-green-700'>Reset password</p>
        <h1 className='mt-3 text-3xl font-semibold tracking-tight text-gray-950'>Criar nova senha</h1>
        <p className='mt-3 text-sm leading-6 text-gray-600'>
          Escolha uma nova senha para continuar acessando sua conta com segurança.
        </p>

        {!token ? (
          <div className='mt-8 rounded-2xl border border-amber-200 bg-amber-50 p-5 text-sm text-amber-900'>
            O link está incompleto. Use o botão do e-mail para abrir esta página novamente.
          </div>
        ) : null}

        <form className='mt-8 space-y-4' onSubmit={handleSubmit}>
          <div>
            <label className='mb-1 block text-sm font-medium text-gray-700' htmlFor='nova-senha'>
              Nova senha
            </label>
            <input
              id='nova-senha'
              name='nova-senha'
              type='password'
              minLength={MIN_PASSWORD_LENGTH}
              value={novaSenha}
              onChange={(event) => setNovaSenha(event.target.value)}
              className='w-full rounded-lg border border-gray-300 px-3 py-2 text-gray-900 outline-none transition focus:border-green-600 focus:ring-2 focus:ring-green-100'
              required
            />
          </div>

          <div>
            <label className='mb-1 block text-sm font-medium text-gray-700' htmlFor='confirmacao-senha'>
              Confirmar senha
            </label>
            <input
              id='confirmacao-senha'
              name='confirmacao-senha'
              type='password'
              minLength={MIN_PASSWORD_LENGTH}
              value={confirmacaoSenha}
              onChange={(event) => setConfirmacaoSenha(event.target.value)}
              className='w-full rounded-lg border border-gray-300 px-3 py-2 text-gray-900 outline-none transition focus:border-green-600 focus:ring-2 focus:ring-green-100'
              required
            />
          </div>

          {errorMessage ? <p className='text-sm text-red-600'>{errorMessage}</p> : null}
          {successMessage ? <p className='text-sm font-medium text-green-700'>{successMessage}</p> : null}

          <Button type='submit' className='w-full' isLoading={isSubmitting} disabled={!token}>
            Redefinir senha
          </Button>
        </form>

        <div className='mt-6 flex flex-col gap-3 sm:flex-row'>
          <Link
            className='inline-flex items-center justify-center rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-green-700'
            href='/login'
          >
            Voltar para login
          </Link>
          <Link
            className='inline-flex items-center justify-center rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-100'
            href='/forgot-password'
          >
            Pedir novo link
          </Link>
        </div>
      </section>
    </main>
  );
}