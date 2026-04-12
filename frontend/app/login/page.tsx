'use client';

import Link from 'next/link';
import { FormEvent, useMemo, useState } from 'react';
import axios from 'axios';
import Button from '@/components/Button';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const validationMessage = useMemo(() => {
    if (!email.trim()) return 'Informe seu e-mail.';
    if (!/\S+@\S+\.\S+/.test(email)) return 'Informe um e-mail válido.';
    if (!senha) return 'Informe sua senha.';
    return '';
  }, [email, senha]);

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
      const payload = new URLSearchParams();
      payload.append('username', email.trim());
      payload.append('password', senha);
      const response = await axios.post(`${API_BASE_URL}/auth/login`, payload, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });
      const accessToken = response.data?.access_token;
      const refreshToken = response.data?.refresh_token;
      if (typeof window !== 'undefined' && accessToken) {
        localStorage.setItem('access_token', accessToken);
      }
      if (typeof window !== 'undefined' && refreshToken) {
        localStorage.setItem('refresh_token', refreshToken);
      }
      setSuccessMessage('Login realizado com sucesso.');
    } catch (error) {
      const detail = axios.isAxiosError<{ detail?: string }>(error) ? error.response?.data?.detail : undefined;
      setErrorMessage(detail ?? 'Não foi possível fazer login. Tente novamente.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className='flex min-h-screen items-center justify-center bg-gray-50 px-4 py-8'>
      <section className='w-full max-w-md rounded-2xl bg-white p-6 shadow-sm sm:p-8'>
        <h1 className='text-2xl font-semibold text-gray-900'>Entrar</h1>
        <p className='mt-2 text-sm text-gray-600'>Acesse sua conta para continuar.</p>

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

          <div>
            <label className='mb-1 block text-sm font-medium text-gray-700' htmlFor='senha'>
              Senha
            </label>
            <input
              id='senha'
              name='senha'
              type='password'
              value={senha}
              onChange={(event) => setSenha(event.target.value)}
              className='w-full rounded-lg border border-gray-300 px-3 py-2 text-gray-900 outline-none transition focus:border-green-600 focus:ring-2 focus:ring-green-100'
              required
            />
          </div>

          <div className='flex justify-end'>
            <Link className='text-sm font-medium text-green-700 hover:underline' href='/forgot-password'>
              Esqueci minha senha
            </Link>
          </div>

          {errorMessage ? <p className='text-sm text-red-600'>{errorMessage}</p> : null}
          {successMessage ? <p className='text-sm text-green-700'>{successMessage}</p> : null}

          <Button type='submit' className='w-full' isLoading={isSubmitting}>
            Entrar
          </Button>
        </form>

        <p className='mt-4 text-sm text-gray-600'>
          Não possui conta?{' '}
          <Link className='font-medium text-green-700 hover:underline' href='/register'>
            Cadastre-se
          </Link>
        </p>
      </section>
    </main>
  );
}
