'use client';

import Link from 'next/link';
import { FormEvent, useMemo, useState } from 'react';
import axios from 'axios';
import Button from '@/components/Button';

const MIN_PASSWORD_LENGTH = 6;
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function RegisterPage() {
  const [nome, setNome] = useState('');
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [confirmacaoSenha, setConfirmacaoSenha] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const validationMessage = useMemo(() => {
    if (!nome.trim()) return 'Informe seu nome.';
    if (!email.trim()) return 'Informe seu e-mail.';
    if (!/\S+@\S+\.\S+/.test(email)) return 'Informe um e-mail válido.';
    if (senha.length < MIN_PASSWORD_LENGTH) return `A senha deve ter pelo menos ${MIN_PASSWORD_LENGTH} caracteres.`;
    if (senha !== confirmacaoSenha) return 'A confirmação de senha não confere.';
    return '';
  }, [confirmacaoSenha, email, nome, senha]);

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
      await axios.post(`${API_BASE_URL}/auth/registrar`, { nome: nome.trim(), email: email.trim(), senha });
      setSuccessMessage('Cadastro realizado com sucesso. Verifique seu e-mail para confirmar a conta.');
      setNome('');
      setEmail('');
      setSenha('');
      setConfirmacaoSenha('');
    } catch (error) {
      const detail = axios.isAxiosError<{ detail?: string }>(error) ? error.response?.data?.detail : undefined;
      setErrorMessage(detail ?? 'Não foi possível concluir o cadastro. Tente novamente.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className='flex min-h-screen items-center justify-center bg-gray-50 px-4 py-8'>
      <section className='w-full max-w-md rounded-2xl bg-white p-6 shadow-sm sm:p-8'>
        <h1 className='text-2xl font-semibold text-gray-900'>Criar conta</h1>
        <p className='mt-2 text-sm text-gray-600'>Preencha seus dados para se cadastrar na plataforma.</p>

        <form className='mt-6 space-y-4' onSubmit={handleSubmit}>
          <div>
            <label className='mb-1 block text-sm font-medium text-gray-700' htmlFor='nome'>
              Nome
            </label>
            <input
              id='nome'
              name='nome'
              type='text'
              value={nome}
              onChange={(event) => setNome(event.target.value)}
              className='w-full rounded-lg border border-gray-300 px-3 py-2 text-gray-900 outline-none transition focus:border-green-600 focus:ring-2 focus:ring-green-100'
              required
            />
          </div>

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
              minLength={MIN_PASSWORD_LENGTH}
              value={senha}
              onChange={(event) => setSenha(event.target.value)}
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
          {successMessage ? <p className='text-sm text-green-700'>{successMessage}</p> : null}

          <Button type='submit' className='w-full' isLoading={isSubmitting}>
            Cadastrar
          </Button>
        </form>

        <p className='mt-4 text-sm text-gray-600'>
          Já tem conta?{' '}
          <Link className='font-medium text-green-700 hover:underline' href='/login'>
            Entrar
          </Link>
        </p>
      </section>
    </main>
  );
}
