'use client';

import Link from 'next/link';
import { FormEvent, useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiFetch, API_URL } from '../../lib/api';

export default function LoginPage() {
  const router = useRouter();
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError('');
    setLoading(true);

    const data = new FormData(event.currentTarget);

    try {
      await apiFetch('/auth/login', {
        method: 'POST',
        body: JSON.stringify({
          email: data.get('email'),
          password: data.get('password'),
        }),
      });

      router.push('/dashboard');
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Autentificarea a eșuat.',
      );
    } finally {
      setLoading(false);
    }
  }

  function loginWith(provider: 'google' | 'facebook') {
    window.location.href = `${API_URL}/auth/${provider}/login`;
  }

  return (
    <main className="auth-shell">
      <section className="auth-card">
        <Link className="brand" href="/">
          ContaAI
        </Link>

        <h1>Autentificare</h1>

        <p className="muted">
          Accesează spațiul contabil securizat.
        </p>

        <div className="oauth-buttons">
          <button
            className="oauth-button google-button"
            type="button"
            onClick={() => loginWith('google')}
          >
            <span className="oauth-icon google-icon">G</span>
            Continuă cu Google
          </button>

          <button
            className="oauth-button facebook-button"
            type="button"
            onClick={() => loginWith('facebook')}
          >
            <span className="oauth-icon facebook-icon">f</span>
            Continuă cu Facebook
          </button>
        </div>

        <div className="auth-divider">
          <span>SAU</span>
        </div>

        <form onSubmit={submit}>
          <label>
            E-mail
            <input
              name="email"
              type="email"
              required
              autoComplete="email"
            />
          </label>

          <label>
            Parolă
            <input
              name="password"
              type="password"
              required
              autoComplete="current-password"
            />
          </label>

          {error && <div className="error">{error}</div>}

          <button disabled={loading}>
            {loading ? 'Se autentifică…' : 'Intră în cont'}
          </button>
        </form>

        <p className="muted center">
          Nu ai cont? <Link href="/register">Creează unul</Link>
        </p>
      </section>
    </main>
  );
}