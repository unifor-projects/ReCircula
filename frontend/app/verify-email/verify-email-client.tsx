'use client';

import { AxiosError } from 'axios';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import { authClient } from '@/services/authClient';

interface VerifyEmailResponse {
  detail: string;
}

export default function VerifyEmailClient() {
  const searchParams = useSearchParams();
  const token = searchParams?.get('token') ?? null;
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    if (!token) {
      setErrorMessage('O link está incompleto. Solicite um novo e-mail de verificação.');
      return;
    }

    let isActive = true;

    async function verifyEmail() {
      setIsSubmitting(true);
      setErrorMessage('');
      setSuccessMessage('');

      try {
        const response = await authClient.post<VerifyEmailResponse>('/auth/verify-email', { token });
        if (!isActive) return;
        setSuccessMessage(response.data?.detail ?? 'E-mail verificado com sucesso.');
      } catch (error) {
        if (!isActive) return;
        const detail = error instanceof AxiosError ? (error.response?.data as { detail?: string } | undefined)?.detail : undefined;
        setErrorMessage(detail ?? 'Não foi possível verificar seu e-mail.');
      } finally {
        if (isActive) {
          setIsSubmitting(false);
        }
      }
    }

    void verifyEmail();

    return () => {
      isActive = false;
    };
  }, [token]);

  return (
    <main className='relative flex min-h-screen items-center justify-center overflow-hidden bg-[radial-gradient(circle_at_top,_rgba(22,163,74,0.18),_transparent_36%),linear-gradient(135deg,_#f8fafc_0%,_#eef7ee_100%)] px-4 py-8 text-gray-900'>
      <div className='absolute inset-x-0 top-0 h-40 bg-gradient-to-b from-green-100/50 to-transparent' />
      <section className='relative w-full max-w-lg rounded-3xl border border-white/70 bg-white/90 p-6 shadow-[0_20px_70px_rgba(15,23,42,0.12)] backdrop-blur sm:p-8'>
        <p className='text-xs font-semibold uppercase tracking-[0.2em] text-green-700'>Verify email</p>
        <h1 className='mt-3 text-3xl font-semibold tracking-tight text-gray-950'>Confirmando seu e-mail</h1>
        <p className='mt-3 text-sm leading-6 text-gray-600'>
          Assim que a confirmação terminar, você já poderá entrar e continuar usando a plataforma.
        </p>

        <div className='mt-8 rounded-2xl border border-gray-200 bg-gray-50 p-5'>
          {isSubmitting ? (
            <p className='text-sm text-gray-700'>Validando o link de confirmação...</p>
          ) : null}
          {successMessage ? <p className='text-sm font-medium text-green-700'>{successMessage}</p> : null}
          {errorMessage ? <p className='text-sm font-medium text-red-600'>{errorMessage}</p> : null}
        </div>

        <div className='mt-6 flex flex-col gap-3 sm:flex-row'>
          <Link
            className='inline-flex items-center justify-center rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-green-700'
            href='/login'
          >
            Ir para login
          </Link>
          <Link
            className='inline-flex items-center justify-center rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-100'
            href='/register'
          >
            Criar conta
          </Link>
        </div>

        <div className='mt-6 border-t border-gray-100 pt-4 text-sm text-gray-600'>
          <p>
            Se este link já expirou, solicite um novo cadastro e verifique o e-mail novamente.
          </p>
          <p className='mt-2'>
            <Link className='font-medium text-green-700 hover:underline' href='/forgot-password'>
              Enviar novo e-mail
            </Link>
          </p>
        </div>
      </section>
    </main>
  );
}