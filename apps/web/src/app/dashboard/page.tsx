'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiFetch } from '../../lib/api';

type User = { first_name: string; last_name: string; email: string };

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    apiFetch<User>('/auth/me').then(setUser).catch(async () => {
      try { await apiFetch('/auth/refresh', { method: 'POST' }); setUser(await apiFetch<User>('/auth/me')); }
      catch { router.replace('/login'); }
    });
  }, [router]);

  async function logout() { await apiFetch('/auth/logout', { method: 'POST' }); router.replace('/login'); }
  if (!user) return <main className="auth-shell"><p>Se verifică sesiunea…</p></main>;

  return <main className="dashboard"><header><div><span className="brand">ContaAI</span><p>Workspace contabil</p></div><button className="secondary" onClick={logout}>Ieșire</button></header>
    <section className="dashboard-card"><span className="eyebrow">Bun venit</span><h1>{user.first_name} {user.last_name}</h1><p>{user.email}</p>
      <div className="cards"><article><b>Identitate</b><span>Autentificare securizată activă</span></article><article><b>Următorul modul</b><span>Organizații și roluri</span></article><article><b>API</b><span>JWT + refresh rotation</span></article></div>
    </section></main>;
}
