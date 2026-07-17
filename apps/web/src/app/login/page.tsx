'use client';

import Link from 'next/link';
import { FormEvent, useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiFetch } from '../../lib/api';

export default function LoginPage() {
  const router = useRouter();
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(''); setLoading(true);
    const data = new FormData(event.currentTarget);
    try {
      await apiFetch('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email: data.get('email'), password: data.get('password') }),
      });
      router.push('/dashboard');
    } catch (err) { setError(err instanceof Error ? err.message : 'Autentificarea a eșuat.'); }
    finally { setLoading(false); }
  }

  return <main className="auth-shell"><section className="auth-card">
    <Link className="brand" href="/">ContaAI</Link>
    <h1>Autentificare</h1><p className="muted">Accesează spațiul contabil securizat.</p>
    <form onSubmit={submit}>
      <label>E-mail<input name="email" type="email" required autoComplete="email" /></label>
      <label>Parolă<input name="password" type="password" required autoComplete="current-password" /></label>
      {error && <div className="error">{error}</div>}
      <button disabled={loading}>{loading ? 'Se autentifică…' : 'Intră în cont'}</button>
    </form>
    <p className="muted center">Nu ai cont? <Link href="/register">Creează unul</Link></p>
  </section></main>;
}
