'use client';

import { FormEvent, useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiFetch } from '../../lib/api';

type User = { first_name: string; last_name: string; email: string };
type Company = { id: string; organization_id: string; name: string; tax_id: string | null; legal_form: string | null; country_code: string };
type Organization = { id: string; name: string; role: { key: string; name: string }; companies: Company[] };
type Workspace = { organizations: Organization[] };

const modules = [
  ['⌂', 'Dashboard'], ['▤', 'Documente'], ['↗', 'Facturi'], ['≡', 'Contabilitate'], ['%', 'TVA'], ['▥', 'Rapoarte'], ['⚙', 'Setări']
];

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [activeCompanyId, setActiveCompanyId] = useState('');
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [showAddCompany, setShowAddCompany] = useState(false);
  const [error, setError] = useState('');

  async function loadWorkspace() {
    const data = await apiFetch<Workspace>('/workspace');
    setWorkspace(data);
    if (!data.organizations.length) setShowOnboarding(true);
    const firstCompany = data.organizations.flatMap(o => o.companies)[0];
    if (firstCompany && !activeCompanyId) setActiveCompanyId(firstCompany.id);
  }

  useEffect(() => {
    apiFetch<User>('/auth/me').then(async current => {
      setUser(current);
      await loadWorkspace();
    }).catch(async () => {
      try {
        await apiFetch('/auth/refresh', { method: 'POST' });
        setUser(await apiFetch<User>('/auth/me'));
        await loadWorkspace();
      } catch { router.replace('/login'); }
    });
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [router]);

  const companies = useMemo(() => workspace?.organizations.flatMap(o => o.companies) ?? [], [workspace]);
  const activeCompany = companies.find(c => c.id === activeCompanyId) ?? companies[0];
  const activeOrganization = workspace?.organizations.find(o => o.id === activeCompany?.organization_id) ?? workspace?.organizations[0];

  async function createOrganization(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError('');
    const form = new FormData(event.currentTarget);
    try {
      await apiFetch('/organizations', { method: 'POST', body: JSON.stringify({
        name: form.get('organizationName'),
        company: { name: form.get('companyName'), tax_id: form.get('taxId') || null, legal_form: form.get('legalForm') || null, country_code: 'RO' }
      }) });
      setShowOnboarding(false); await loadWorkspace();
    } catch (e) { setError(e instanceof Error ? e.message : 'A apărut o eroare.'); }
  }

  async function addCompany(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError('');
    if (!activeOrganization) return;
    const form = new FormData(event.currentTarget);
    try {
      const company = await apiFetch<Company>(`/organizations/${activeOrganization.id}/companies`, { method: 'POST', body: JSON.stringify({
        name: form.get('companyName'), tax_id: form.get('taxId') || null, legal_form: form.get('legalForm') || null, country_code: 'RO'
      }) });
      setShowAddCompany(false); await loadWorkspace(); setActiveCompanyId(company.id);
    } catch (e) { setError(e instanceof Error ? e.message : 'A apărut o eroare.'); }
  }

  async function logout() { await apiFetch('/auth/logout', { method: 'POST' }); router.replace('/login'); }
  if (!user || !workspace) return <main className="auth-shell"><p>Se pregătește workspace-ul…</p></main>;

  return <div className="erp-shell">
    <aside className="sidebar">
      <div className="logo-mark"><span>CA</span><strong>ContaAI</strong></div>
      <nav>{modules.map(([icon, label], index) => <button key={label} className={index === 0 ? 'nav-item active' : 'nav-item'}><span>{icon}</span>{label}</button>)}</nav>
      <div className="sidebar-bottom"><div className="ai-status"><span className="pulse"/><div><strong>AI Engine</strong><small>Pregătit pentru documente</small></div></div></div>
    </aside>

    <div className="erp-main">
      <header className="topbar">
        <div className="company-switcher">
          <label>Companie activă</label>
          <select value={activeCompany?.id ?? ''} onChange={e => setActiveCompanyId(e.target.value)} disabled={!companies.length}>
            {!companies.length && <option>Nicio companie</option>}
            {workspace.organizations.map(org => <optgroup key={org.id} label={org.name}>{org.companies.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}</optgroup>)}
          </select>
        </div>
        <div className="top-actions"><button className="icon-button">⌕</button><button className="icon-button">◔</button><div className="user-chip"><span>{user.first_name[0]}{user.last_name[0]}</span><div><strong>{user.first_name} {user.last_name}</strong><small>{activeOrganization?.role.name ?? 'Utilizator'}</small></div></div><button className="ghost-button" onClick={logout}>Ieșire</button></div>
      </header>

      <main className="content-area">
        <div className="page-heading"><div><p className="eyebrow-text">PREZENTARE GENERALĂ</p><h1>Bun venit, {user.first_name}</h1><p>Ai control asupra activității contabile dintr-un singur loc.</p></div><div className="heading-actions"><button className="secondary" onClick={() => setShowAddCompany(true)}>+ Companie</button><button>+ Încarcă document</button></div></div>

        <section className="metric-grid">
          <article><div><small>Documente luna aceasta</small><strong>0</strong><span>În așteptarea primului import</span></div><i>▤</i></article>
          <article><div><small>De procesat</small><strong>0</strong><span>Inbox-ul este curat</span></div><i>✓</i></article>
          <article><div><small>TVA estimat</small><strong>0 lei</strong><span>Perioada curentă</span></div><i>%</i></article>
          <article><div><small>Companii active</small><strong>{companies.length}</strong><span>{workspace.organizations.length} organizații</span></div><i>▦</i></article>
        </section>

        <section className="dashboard-grid">
          <article className="panel activity-panel"><div className="panel-title"><div><h2>Activitate recentă</h2><p>Ultimele acțiuni din workspace</p></div><button className="link-button">Vezi tot</button></div><div className="empty-state"><div>↥</div><h3>Încarcă primul document</h3><p>Facturile și documentele procesate vor apărea aici.</p><button>Încarcă document</button></div></article>
          <article className="panel quick-panel"><div className="panel-title"><div><h2>Acțiuni rapide</h2><p>Continuă configurarea ContaAI</p></div></div><button onClick={() => setShowAddCompany(true)}><span>▦</span><div><strong>Adaugă o companie</strong><small>Creează un nou dosar contabil</small></div><b>›</b></button><button><span>⇧</span><div><strong>Importă documente</strong><small>PDF, imagini sau arhive</small></div><b>›</b></button><button><span>⚙</span><div><strong>Configurează contabilitatea</strong><small>Plan de conturi și perioade</small></div><b>›</b></button></article>
        </section>
      </main>
    </div>

    {(showOnboarding || showAddCompany) && <div className="modal-backdrop"><div className="modal-card"><div className="modal-head"><div><span className="eyebrow-text">{showOnboarding ? 'CONFIGURARE INIȚIALĂ' : 'COMPANIE NOUĂ'}</span><h2>{showOnboarding ? 'Creează workspace-ul tău' : 'Adaugă o companie'}</h2><p>{showOnboarding ? 'Configurează organizația și prima companie.' : `Compania va fi adăugată în ${activeOrganization?.name}.`}</p></div>{!showOnboarding && <button className="modal-close" onClick={() => setShowAddCompany(false)}>×</button>}</div>
      <form onSubmit={showOnboarding ? createOrganization : addCompany}>
        {showOnboarding && <label>Numele organizației<input name="organizationName" placeholder="Ex: Cabinet Robert Mole" required minLength={2}/></label>}
        <label>Numele companiei<input name="companyName" placeholder="Ex: Demo Consulting SRL" required minLength={2}/></label>
        <div className="two-cols"><label>CUI / CIF<input name="taxId" placeholder="RO12345678"/></label><label>Forma juridică<select name="legalForm"><option value="SRL">SRL</option><option value="PFA">PFA</option><option value="CMI">Cabinet medical</option><option value="SA">SA</option><option value="">Alta</option></select></label></div>
        {error && <p className="error">{error}</p>}
        <button type="submit">{showOnboarding ? 'Creează workspace-ul' : 'Adaugă compania'}</button>
      </form></div></div>}
  </div>;
}
