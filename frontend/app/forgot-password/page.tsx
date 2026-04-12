'use client';

import Link from 'next/link';
import { FormEvent, useMemo, useState } from 'react';
import { AxiosError } from 'axios';
import Button from '@/components/Button';
import { authClient, EMAIL_PATTERN } from '@/services/authClient';

interface ForgotPasswordResponse {
  detail: string;
}

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const validationMessage = useMemo(() => {
    if (!email.trim()) return 'Informe seu e-mail.';
    if (!EMAIL_PATTERN.test(email)) return 'Informe um e-mail válido.';
    return '';
  }, [email]);

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
      const response = await authClient.post<ForgotPasswordResponse>('/auth/forgot-password', { email: email.trim() });
      const detail = response.data?.detail;
      setSuccessMessage(detail ?? 'Se o e-mail estiver cadastrado, enviaremos as instruções de recuperação.');
    } catch (error) {
      const detail = error instanceof AxiosError ? (error.response?.data as { detail?: string } | undefined)?.detail : undefined;
      setErrorMessage(detail ?? 'Não foi possível processar sua solicitação.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className='flex min-h-screen items-center justify-center bg-gray-50 px-4 py-8'>
      <section className='w-full max-w-md rounded-2xl bg-white p-6 shadow-sm sm:p-8'>
        <h1 className='text-2xl font-semibold text-gray-900'>Recuperar senha</h1>
        <p className='mt-2 text-sm text-gray-600'>Informe seu e-mail para receber instruções de redefinição.</p>

        <form className='mt-6 space-y-4' onSubmit={handleSubmit}>
          <div>
            <label className='mb-1 block text-sm font-medium text-gray-700' htmlFor='email'>
              E-mail
            </label>
            <input
              id='email'
              name='email'
              type='email'
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              className='w-full rounded-lg border border-gray-300 px-3 py-2 text-gray-900 outline-none transition focus:border-green-600 focus:ring-2 focus:ring-green-100'
              required
            />
          </div>

          {errorMessage ? <p className='text-sm text-red-600'>{errorMessage}</p> : null}
          {successMessage ? <p className='text-sm text-green-700'>{successMessage}</p> : null}

          <Button type='submit' className='w-full' isLoading={isSubmitting}>
            Enviar instruções
          </Button>
        </form>

        <p className='mt-4 text-sm text-gray-600'>
          Lembrou sua senha?{' '}
          <Link className='font-medium text-green-700 hover:underline' href='/login'>
            Voltar para login
          </Link>
        </p>
      </section>
    </main>
  );
}
