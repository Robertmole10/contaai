'use client';

import Link from 'next/link';
import { FormEvent, useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiFetch } from '../../lib/api';

export default function RegisterPage() {
  const router = useRouter();
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError('');
    const data = new FormData(event.currentTarget);
    if (data.get('password') !== data.get('confirm')) { setError('Parolele nu coincid.'); return; }
    setLoading(true);
    try {
      await apiFetch('/auth/register', { method: 'POST', body: JSON.stringify({
        first_name: data.get('first_name'), last_name: data.get('last_name'),
        email: data.get('email'), password: data.get('password'),
      }) });
      router.push('/dashboard');
    } catch (err) { setError(err instanceof Error ? err.message : 'Crearea contului a eșuat.'); }
    finally { setLoading(false); }
  }

  return <main className="auth-shell"><section className="auth-card wide">
    <Link className="brand" href="/">ContaAI</Link><h1>Creează cont</h1>
    <p className="muted">Primul pas către administrarea organizației tale.</p>
    <form onSubmit={submit}>
      <div className="two-cols"><label>Prenume<input name="first_name" required /></label><label>Nume<input name="last_name" required /></label></div>
      <label>E-mail<input name="email" type="email" required autoComplete="email" /></label>
      <label>Parolă<input name="password" type="password" minLength={10} required autoComplete="new-password" /></label>
      <label>Confirmă parola<input name="confirm" type="password" minLength={10} required autoComplete="new-password" /></label>
      {error && <div className="error">{error}</div>}
      <button disabled={loading}>{loading ? 'Se creează…' : 'Creează contul'}</button>
    </form>
    <p className="muted center">Ai deja cont? <Link href="/login">Autentifică-te</Link></p>
  </section></main>;
}
