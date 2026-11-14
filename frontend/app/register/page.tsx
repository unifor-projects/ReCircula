'use client';

import Link from 'next/link';
import { FormEvent, useMemo, useState } from 'react';
import { AxiosError } from 'axios';
import { Check, Lock, Mail, MailCheck, User } from 'lucide-react';
import AuthInput from '@/components/AuthInput';
import AuthShell from '@/components/AuthShell';
import Button from '@/components/Button';
import { authClient, EMAIL_PATTERN } from '@/services/authClient';

const MIN_PASSWORD_LENGTH = 6;

function Requisito({ ok, children }: { ok: boolean; children: string }) {
  return (
    <li className={`flex items-center gap-1.5 transition-colors ${ok ? 'text-green-700' : 'text-gray-500'}`}>
      <span
        className={`flex h-4 w-4 items-center justify-center rounded-full transition-colors ${ok ? 'bg-green-600 text-white' : 'bg-gray-200'}`}
      >
        {ok && <Check size={11} strokeWidth={3} aria-hidden='true' />}
      </span>
      {children}
      <span className='sr-only'>{ok ? ' (atendido)' : ' (pendente)'}</span>
    </li>
  );
}

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
    if (!EMAIL_PATTERN.test(email)) return 'Informe um e-mail válido.';
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
      await authClient.post('/auth/registrar', { nome: nome.trim(), email: email.trim(), senha });
      setSuccessMessage('Cadastro realizado com sucesso. Verifique seu e-mail para confirmar a conta.');
      setNome('');
      setEmail('');
      setSenha('');
      setConfirmacaoSenha('');
    } catch (error) {
      const detail = error instanceof AxiosError ? (error.response?.data as { detail?: string } | undefined)?.detail : undefined;
      setErrorMessage(detail ?? 'Não foi possível concluir o cadastro. Tente novamente.');
    } finally {
      setIsSubmitting(false);
    }
  }

  if (successMessage) {
    return (
      <AuthShell title='Quase lá!' subtitle='Falta só confirmar seu e-mail.'>
        <div className='rounded-2xl border border-green-200 bg-green-50 p-6 text-center'>
          <MailCheck className='mx-auto text-green-600' size={40} aria-hidden='true' />
          <p className='mt-4 font-medium text-green-800' role='status'>
            {successMessage}
          </p>
          <p className='mt-2 text-sm text-green-700'>Não achou? Confira a caixa de spam.</p>
        </div>
        <Link
          href='/login'
          className='mt-6 flex w-full items-center justify-center rounded-lg bg-green-600 py-3 text-base font-medium text-white transition-colors hover:bg-green-700 focus-visible:ring-2 focus-visible:ring-green-500 focus-visible:ring-offset-2'
        >
          Ir para o login
        </Link>
      </AuthShell>
    );
  }

  return (
    <AuthShell title='Crie sua conta' subtitle='É grátis e leva menos de um minuto.'>
      <form className='space-y-5' onSubmit={handleSubmit} noValidate>
        <AuthInput
          id='nome'
          label='Nome'
          icon={User}
          autoComplete='name'
          placeholder='Como quer ser chamado'
          value={nome}
          onChange={(event) => setNome(event.target.value)}
          required
        />
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
        <AuthInput
          id='senha'
          label='Senha'
          icon={Lock}
          type='password'
          autoComplete='new-password'
          placeholder='Crie uma senha'
          hint={
            <ul className='space-y-1'>
              <Requisito ok={senha.length >= MIN_PASSWORD_LENGTH}>{`Pelo menos ${MIN_PASSWORD_LENGTH} caracteres`}</Requisito>
              <Requisito ok={!!senha && senha === confirmacaoSenha}>As senhas conferem</Requisito>
            </ul>
          }
          minLength={MIN_PASSWORD_LENGTH}
          value={senha}
          onChange={(event) => setSenha(event.target.value)}
          required
        />
        <AuthInput
          id='confirmacao-senha'
          label='Confirmar senha'
          icon={Lock}
          type='password'
          autoComplete='new-password'
          placeholder='Repita a senha'
          minLength={MIN_PASSWORD_LENGTH}
          value={confirmacaoSenha}
          onChange={(event) => setConfirmacaoSenha(event.target.value)}
          required
        />

        {errorMessage ? (
          <p role='alert' className='rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700'>
            {errorMessage}
          </p>
        ) : null}

        <Button type='submit' className='w-full py-3 text-base' isLoading={isSubmitting}>
          Criar conta
        </Button>
      </form>

      <p className='mt-8 text-center text-sm text-gray-600'>
        Já tem conta?{' '}
        <Link className='font-semibold text-green-700 hover:underline' href='/login'>
          Entrar
        </Link>
      </p>
    </AuthShell>
  );
}
