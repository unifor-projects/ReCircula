import { Suspense } from 'react';
import ResetPasswordClient from './reset-password-client';

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={null}>
      <ResetPasswordClient />
    </Suspense>
  );
}
