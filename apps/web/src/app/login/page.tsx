'use client';

import Link from 'next/link';
import { FormEvent, useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import {
  ArrowRight,
  BrainCircuit,
  Eye,
  EyeOff,
  LockKeyhole,
  Mail,
  ShieldCheck,
  Sparkles,
} from 'lucide-react';
import { apiFetch, API_URL } from '../../lib/api';

export default function LoginPage() {
  const router = useRouter();

  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

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
      router.refresh();
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
    <main className="ca-auth-page">
      <div className="ca-auth-glow ca-auth-glow-one" />
      <div className="ca-auth-glow ca-auth-glow-two" />

      <section className="ca-auth-layout">
        <motion.div
          className="ca-auth-intro"
          initial={{ opacity: 0, x: -24 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.55 }}
        >
          <Link className="ca-auth-brand" href="/">
            <span className="ca-auth-brand-icon">
              <BrainCircuit size={25} />
            </span>

            <span>
              Conta<span>AI</span>
            </span>
          </Link>

          <div className="ca-auth-kicker">
            <Sparkles size={15} />
            Contabilitate inteligentă
          </div>

          <h1>
            Control financiar.
            <br />
            Decizii mai bune.
          </h1>

          <p className="ca-auth-description">
            Platforma modernă pentru automatizarea documentelor,
            contabilității și conformității fiscale.
          </p>

          <div className="ca-auth-benefits">
            <div>
              <ShieldCheck size={20} />
              <span>Date protejate și acces securizat</span>
            </div>

            <div>
              <BrainCircuit size={20} />
              <span>Analiză contabilă asistată de AI</span>
            </div>
          </div>

          <p className="ca-auth-version">
            ContaAI · Financial Intelligence Platform
          </p>
        </motion.div>

        <motion.section
          className="ca-auth-card"
          initial={{ opacity: 0, y: 24, scale: 0.985 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.08 }}
        >
          <div className="ca-auth-card-header">
            <span className="ca-auth-security">
              <LockKeyhole size={15} />
              Conexiune securizată
            </span>

            <h2>Bine ai revenit</h2>

            <p>
              Autentifică-te pentru a accesa spațiul tău contabil.
            </p>
          </div>

          <div className="ca-auth-socials ca-auth-socials-single">
            <button
              className="ca-auth-social-button ca-auth-google-button"
              type="button"
              onClick={() => loginWith('google')}
            >
              <svg
                className="ca-auth-google-logo"
                width="20"
                height="20"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  fill="#4285F4"
                  d="M21.6 12.23c0-.71-.06-1.4-.18-2.07H12v3.92h5.38a4.6 4.6 0 0 1-2 3.02v2.54h3.24c1.9-1.75 2.98-4.33 2.98-7.41Z"
                />
                <path
                  fill="#34A853"
                  d="M12 22c2.7 0 4.97-.9 6.63-2.42l-3.24-2.53c-.9.6-2.05.96-3.39.96-2.61 0-4.82-1.76-5.61-4.13H3.04v2.61A10 10 0 0 0 12 22Z"
                />
                <path
                  fill="#FBBC05"
                  d="M6.39 13.88A6 6 0 0 1 6.08 12c0-.65.11-1.28.31-1.88V7.51H3.04A10 10 0 0 0 2 12c0 1.61.38 3.13 1.04 4.49l3.35-2.61Z"
                />
                <path
                  fill="#EA4335"
                  d="M12 5.99c1.47 0 2.79.51 3.83 1.5l2.87-2.88A9.65 9.65 0 0 0 12 2a10 10 0 0 0-8.96 5.51l3.35 2.61C7.18 7.75 9.39 5.99 12 5.99Z"
                />
              </svg>

              <span>Continuă cu Google</span>
            </button>
          </div>

          <div className="ca-auth-divider">
            <span>SAU CONTINUĂ CU E-MAIL</span>
          </div>

          <form className="ca-auth-form" onSubmit={submit}>
            <label>
              <span>Adresă de e-mail</span>

              <div className="ca-auth-input-wrapper">
                <Mail size={18} />

                <input
                  name="email"
                  type="email"
                  placeholder="nume@companie.ro"
                  required
                  autoComplete="email"
                />
              </div>
            </label>

            <label>
              <span>Parolă</span>

              <div className="ca-auth-input-wrapper">
                <LockKeyhole size={18} />

                <input
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Introdu parola"
                  required
                  autoComplete="current-password"
                />

                <button
                  className="ca-auth-password-toggle"
                  type="button"
                  onClick={() => setShowPassword((value) => !value)}
                  aria-label={
                    showPassword
                      ? 'Ascunde parola'
                      : 'Afișează parola'
                  }
                >
                  {showPassword ? (
                    <EyeOff size={18} />
                  ) : (
                    <Eye size={18} />
                  )}
                </button>
              </div>
            </label>

            <div className="ca-auth-form-options">
              <label className="ca-auth-remember">
                <input type="checkbox" />
                <span>Ține-mă minte</span>
              </label>

              <Link href="/forgot-password">
                Ai uitat parola?
              </Link>
            </div>

            {error && (
              <div className="ca-auth-error" role="alert">
                {error}
              </div>
            )}

            <button
              className="ca-auth-submit"
              type="submit"
              disabled={loading}
            >
              <span>
                {loading
                  ? 'Se autentifică…'
                  : 'Intră în cont'}
              </span>

              {!loading && <ArrowRight size={19} />}
            </button>
          </form>

          <p className="ca-auth-register">
            Nu ai încă un cont?
            {' '}
            <Link href="/register">Creează un cont</Link>
          </p>
        </motion.section>
      </section>
    </main>
  );
}
