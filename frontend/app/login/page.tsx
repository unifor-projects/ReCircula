'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { FormEvent, useMemo, useState } from 'react';
import { AxiosError } from 'axios';
import { Lock, Mail } from 'lucide-react';
import AuthInput from '@/components/AuthInput';
import AuthShell from '@/components/AuthShell';
import Button from '@/components/Button';
import { useAuth } from '@/contexts/AuthContext';
import { authClient, EMAIL_PATTERN } from '@/services/authClient';
import { User } from '@/types';

interface LoginResponse {
  access_token: string;
  refresh_token: string;
}

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isResending, setIsResending] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [resendMessage, setResendMessage] = useState('');

  const validationMessage = useMemo(() => {
    if (!email.trim()) return 'Informe seu e-mail.';
    if (!EMAIL_PATTERN.test(email)) return 'Informe um e-mail válido.';
    if (!senha) return 'Informe sua senha.';
    return '';
  }, [email, senha]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErrorMessage('');
    setResendMessage('');

    if (validationMessage) {
      setErrorMessage(validationMessage);
      return;
    }

    setIsSubmitting(true);

    try {
      const payload = new URLSearchParams();
      payload.append('username', email.trim());
      payload.append('password', senha);
      const { data } = await authClient.post<LoginResponse>('/auth/login', payload, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });
      const profileResponse = await authClient.get<User>('/usuarios/me', {
        headers: { Authorization: `Bearer ${data.access_token}` },
      });
      login(data.access_token, data.refresh_token, profileResponse.data);
      const next = new URLSearchParams(window.location.search).get('next');
      router.push(next?.startsWith('/') && !next.startsWith('//') ? next : '/anuncios');
    } catch (error) {
      const detail = error instanceof AxiosError ? (error.response?.data as { detail?: string } | undefined)?.detail : undefined;
      setErrorMessage(detail ?? 'Não foi possível fazer login. Tente novamente.');
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleResendVerification() {
    setResendMessage('');
    setIsResending(true);

    try {
      const { data } = await authClient.post<{ detail: string }>('/auth/resend-verification', {
        email: email.trim(),
      });
      setResendMessage(data.detail);
    } catch (error) {
      const detail = error instanceof AxiosError ? (error.response?.data as { detail?: string } | undefined)?.detail : undefined;
      setResendMessage(detail ?? 'Não foi possível reenviar o e-mail. Tente novamente.');
    } finally {
      setIsResending(false);
    }
  }

  return (
    <AuthShell title='Bem-vindo de volta' subtitle='Entre para anunciar, conversar e acompanhar suas doações.'>
      <form className='space-y-5' onSubmit={handleSubmit} noValidate>
        <AuthInput
          id='email'
          label='E-mail'
          icon={Mail}
          type='email'
          autoComplete='email'
          spellCheck={false}
          autoCapitalize='none'
          placeholder='voce@email.com'
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          required
        />
        <div>
          <AuthInput
            id='senha'
            label='Senha'
            icon={Lock}
            type='password'
            autoComplete='current-password'
            placeholder='Sua senha'
            value={senha}
            onChange={(event) => setSenha(event.target.value)}
            required
          />
          <div className='mt-2 flex justify-end'>
            <Link className='text-sm font-medium text-green-700 hover:underline' href='/forgot-password'>
              Esqueci minha senha
            </Link>
          </div>
        </div>

        {errorMessage ? <p role='alert' className='text-sm text-red-600'>{errorMessage}</p> : null}
        {errorMessage === 'E-mail ainda não verificado' ? (
          <div className='space-y-2'>
            <Button type='button' variant='outline' className='w-full' isLoading={isResending} onClick={handleResendVerification}>
              Reenviar e-mail de verificação
            </Button>
            {resendMessage ? <p className='text-sm text-green-700'>{resendMessage}</p> : null}
          </div>
        ) : null}
        <Button type='submit' className='w-full' isLoading={isSubmitting}>
          Entrar
        </Button>
      </form>

      <p className='mt-8 text-center text-sm text-gray-600'>
        Ainda não tem conta?{' '}
        <Link className='font-semibold text-green-700 hover:underline' href='/register'>
          Cadastre-se grátis
        </Link>
      </p>
    </AuthShell>
  );
}
