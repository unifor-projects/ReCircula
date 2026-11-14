'use client';

import { Eye, EyeOff, type LucideIcon } from 'lucide-react';
import { useState, type InputHTMLAttributes, type ReactNode } from 'react';

interface AuthInputProps extends InputHTMLAttributes<HTMLInputElement> {
  id: string;
  label: string;
  icon: LucideIcon;
  hint?: ReactNode;
}

export default function AuthInput({ id, label, icon: Icon, hint, type = 'text', ...props }: AuthInputProps) {
  const [visivel, setVisivel] = useState(false);
  const isPassword = type === 'password';

  return (
    <div>
      <label className='mb-1.5 block text-sm font-medium text-gray-700' htmlFor={id}>
        {label}
      </label>
      <div className='relative'>
        <Icon size={18} aria-hidden='true' className='pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-gray-400' />
        <input
          id={id}
          name={id}
          type={isPassword && visivel ? 'text' : type}
          aria-describedby={hint ? `${id}-hint` : undefined}
          className={`w-full rounded-xl border border-gray-300 bg-white py-3 pl-10 text-gray-900 outline-none transition placeholder:text-gray-400 focus:border-green-600 focus:ring-4 focus:ring-green-100 ${isPassword ? 'pr-12' : 'pr-3'}`}
          {...props}
        />
        {isPassword && (
          <button
            type='button'
            onClick={() => setVisivel((v) => !v)}
            aria-label={visivel ? 'Ocultar senha' : 'Mostrar senha'}
            aria-pressed={visivel}
            className='absolute right-1 top-1/2 flex h-10 w-10 -translate-y-1/2 items-center justify-center rounded-lg text-gray-400 transition hover:text-gray-700 focus-visible:ring-2 focus-visible:ring-green-500'
          >
            {visivel ? <EyeOff size={18} /> : <Eye size={18} />}
          </button>
        )}
      </div>
      {hint && (
        <div id={`${id}-hint`} className='mt-1.5 text-xs text-gray-500'>
          {hint}
        </div>
      )}
    </div>
  );
}
