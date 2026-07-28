'use client';

import { FormEvent, useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import {
  Activity, Banknote, Bell, BookOpen, Bot, Building2, CheckCircle2,
  ChevronDown, CircleAlert, FileText, Gauge, HelpCircle, LayoutDashboard,
  LogOut, Menu, Plus, ReceiptText, Search, Settings, ShieldCheck,
  Sparkles, TrendingUp, Upload, Users, WalletCards, X,
} from 'lucide-react';
import { ThemeToggle } from '../../components/theme-toggle';
import { apiFetch } from '../../lib/api';

type User = { first_name: string; last_name: string; email: string };
type Company = { id: string; organization_id: string; name: string; tax_id: string | null; legal_form: string | null; country_code: string };
type Organization = { id: string; name: string; role: { key: string; name: string }; companies: Company[] };
type Workspace = { organizations: Organization[] };
type ViewKey = 'dashboard' | 'workspace' | 'companies' | 'members';

const primaryNavigation = [
  { key: 'dashboard' as ViewKey, label: 'Dashboard', icon: LayoutDashboard },
  { key: 'workspace' as ViewKey, label: 'Workspace', icon: Building2 },
  { key: 'companies' as ViewKey, label: 'Companii', icon: WalletCards },
  { key: 'members' as ViewKey, label: 'Membri', icon: Users },
];

const productNavigation = [
  { label: 'Documente', icon: FileText, badge: '12' },
  { label: 'Bancă', icon: Banknote, badge: '3' },
  { label: 'Facturi', icon: ReceiptText },
  { label: 'Contabilitate', icon: BookOpen },
  { label: 'Fiscal Intelligence', icon: ShieldCheck, badge: 'Nou' },
  { label: 'Asistent AI', icon: Bot },
  { label: 'Rapoarte', icon: TrendingUp },
];

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [activeOrganizationId, setActiveOrganizationId] = useState('');
  const [activeCompanyId, setActiveCompanyId] = useState('');
  const [activeView, setActiveView] = useState<ViewKey>('dashboard');
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [showAddCompany, setShowAddCompany] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [error, setError] = useState('');

  async function loadWorkspace() {
    const data = await apiFetch<Workspace>('/workspace');
    setWorkspace(data);
    if (!data.organizations.length) setShowOnboarding(true);
    const firstOrganization = data.organizations[0];
    if (firstOrganization && !activeOrganizationId) setActiveOrganizationId(firstOrganization.id);
    const firstCompany = firstOrganization?.companies[0] ?? data.organizations.flatMap(o => o.companies)[0];
    if (firstCompany && !activeCompanyId) setActiveCompanyId(firstCompany.id);
  }

  useEffect(() => {
    apiFetch<User>('/auth/me')
      .then(async currentUser => { setUser(currentUser); await loadWorkspace(); })
      .catch(async () => {
        try {
          await apiFetch('/auth/refresh', { method: 'POST' });
          setUser(await apiFetch<User>('/auth/me'));
          await loadWorkspace();
        } catch { router.replace('/login'); }
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [router]);

  const activeOrganization = workspace?.organizations.find(o => o.id === activeOrganizationId) ?? workspace?.organizations[0];
  const companies = useMemo(() => activeOrganization?.companies ?? [], [activeOrganization]);
  const activeCompany = companies.find(c => c.id === activeCompanyId) ?? companies[0];
  const canManageCompanies = ['owner', 'admin'].includes(activeOrganization?.role.key ?? '');

  function changeOrganization(id: string) {
    setActiveOrganizationId(id);
    const next = workspace?.organizations.find(o => o.id === id);
    setActiveCompanyId(next?.companies[0]?.id ?? '');
  }

  async function createOrganization(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError('');
    const form = new FormData(event.currentTarget);
    try {
      await apiFetch('/organizations', { method: 'POST', body: JSON.stringify({
        name: form.get('organizationName'),
        company: { name: form.get('companyName'), tax_id: form.get('taxId') || null, legal_form: form.get('legalForm') || null, country_code: 'RO' },
      }) });
      setShowOnboarding(false); await loadWorkspace();
    } catch (e) { setError(e instanceof Error ? e.message : 'A apărut o eroare.'); }
  }

  async function addCompany(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError('');
    if (!activeOrganization) return;
    const form = new FormData(event.currentTarget);
    try {
      const company = await apiFetch<Company>(`/organizations/${activeOrganization.id}/companies`, {
        method: 'POST', body: JSON.stringify({ name: form.get('companyName'), tax_id: form.get('taxId') || null, legal_form: form.get('legalForm') || null, country_code: 'RO' }),
      });
      setShowAddCompany(false); await loadWorkspace(); setActiveCompanyId(company.id);
    } catch (e) { setError(e instanceof Error ? e.message : 'A apărut o eroare.'); }
  }

  async function logout() { await apiFetch('/auth/logout', { method: 'POST' }); router.replace('/login'); }

  if (!user || !workspace) return <main className="workspace-loading"><div className="loading-logo"><Sparkles size={22}/></div><p>Se pregătește workspace-ul ContaAI…</p></main>;
  const initials = `${user.first_name.charAt(0)}${user.last_name.charAt(0)}`;

  return (
    <div className="ca-product-shell">
      <aside className={`ca-sidebar ${mobileMenuOpen ? 'is-open' : ''}`}>
        <div className="ca-sidebar-brand"><span><Sparkles size={20}/></span><div><strong>ContaAI</strong><small>Financial Intelligence Platform</small></div><button onClick={() => setMobileMenuOpen(false)} aria-label="Închide"><X size={19}/></button></div>
        <div className="ca-sidebar-context">
          <label>Workspace</label>
          <div className="ca-select-shell"><Building2 size={16}/><select value={activeOrganization?.id ?? ''} onChange={e => changeOrganization(e.target.value)}>{workspace.organizations.map(o => <option key={o.id} value={o.id}>{o.name}</option>)}</select><ChevronDown size={15}/></div>
          <span className="ca-role-pill">{activeOrganization?.role.name ?? 'Utilizator'}</span>
        </div>
        <nav className="ca-sidebar-nav">
          <p>Administrare</p>
          {primaryNavigation.map(item => { const Icon = item.icon; return <button key={item.key} className={activeView === item.key ? 'active' : ''} onClick={() => { setActiveView(item.key); setMobileMenuOpen(false); }}><Icon size={18}/><span>{item.label}</span></button>; })}
          <p>Produse</p>
          {productNavigation.map(item => { const Icon = item.icon; return <button key={item.label}><Icon size={18}/><span>{item.label}</span>{item.badge && <small>{item.badge}</small>}</button>; })}
        </nav>
        <div className="ca-sidebar-bottom">
          <button><Settings size={18}/><span>Setări</span></button>
          <button><HelpCircle size={18}/><span>Ajutor</span></button>
          <div className="ca-ai-status"><span><Bot size={17}/></span><div><strong>AI Engine local</strong><small><i/>Ollama · disponibil</small></div></div>
        </div>
      </aside>
      {mobileMenuOpen && <button className="ca-mobile-overlay" onClick={() => setMobileMenuOpen(false)} aria-label="Închide meniul"/>}

      <div className="ca-product-main">
        <header className="ca-topbar">
          <div className="ca-topbar-left"><button className="ca-mobile-menu" onClick={() => setMobileMenuOpen(true)}><Menu size={20}/></button><div className="ca-company-switcher"><label>Companie activă</label><div className="ca-select-shell"><Building2 size={16}/><select value={activeCompany?.id ?? ''} onChange={e => setActiveCompanyId(e.target.value)} disabled={!companies.length}>{!companies.length && <option>Nicio companie</option>}{companies.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}</select><ChevronDown size={15}/></div></div></div>
          <div className="ca-topbar-actions"><button className="ca-search"><Search size={17}/><span>Caută</span><kbd>⌘ K</kbd></button><button className="ca-ai-button"><Sparkles size={16}/>Întreabă ContaAI</button><ThemeToggle/><button className="ca-icon-button"><Bell size={18}/></button><div className="ca-user"><span>{initials}</span><div><strong>{user.first_name} {user.last_name}</strong><small>{activeOrganization?.role.name ?? 'Utilizator'}</small></div></div><button className="ca-icon-button" onClick={logout}><LogOut size={18}/></button></div>
        </header>

        <main className="ca-content">
          {activeView === 'dashboard' && <DashboardView user={user} company={activeCompany} onAdd={() => setShowAddCompany(true)} canManage={canManageCompanies}/>} 
          {activeView === 'workspace' && <WorkspaceView organization={activeOrganization}/>} 
          {activeView === 'companies' && <CompaniesView companies={companies} canManage={canManageCompanies} onAdd={() => setShowAddCompany(true)}/>} 
          {activeView === 'members' && <MembersView user={user} organization={activeOrganization}/>} 
        </main>
      </div>

      {(showOnboarding || showAddCompany) && <div className="ca-modal-backdrop"><motion.div className="ca-modal" initial={{opacity:0,y:20,scale:.98}} animate={{opacity:1,y:0,scale:1}}>
        <div className="ca-modal-header"><div><span>{showOnboarding ? 'Configurare inițială' : 'Companie nouă'}</span><h2>{showOnboarding ? 'Creează workspace-ul tău' : 'Adaugă o companie'}</h2><p>{showOnboarding ? 'Configurează organizația și prima companie.' : `Compania va fi adăugată în ${activeOrganization?.name ?? 'workspace'}.`}</p></div>{!showOnboarding && <button className="ca-icon-button" onClick={() => setShowAddCompany(false)}><X size={19}/></button>}</div>
        <form className="ca-form" onSubmit={showOnboarding ? createOrganization : addCompany}>
          {showOnboarding && <label><span>Numele organizației</span><input name="organizationName" placeholder="Ex: Robert Medical Group" required minLength={2}/></label>}
          <label><span>Numele companiei</span><input name="companyName" placeholder="Ex: Demo Consulting SRL" required minLength={2}/></label>
          <div className="ca-form-grid"><label><span>CUI / CIF</span><input name="taxId" placeholder="RO12345678"/></label><label><span>Forma juridică</span><select name="legalForm"><option value="SRL">SRL</option><option value="PFA">PFA</option><option value="CMI">Cabinet medical</option><option value="SA">SA</option><option value="">Alta</option></select></label></div>
          {error && <p className="ca-form-error">{error}</p>}
          <div className="ca-modal-actions">{!showOnboarding && <button type="button" className="ca-button secondary" onClick={() => setShowAddCompany(false)}>Renunță</button>}<button className="ca-button primary" type="submit"><Plus size={16}/>{showOnboarding ? 'Creează workspace-ul' : 'Adaugă compania'}</button></div>
        </form>
      </motion.div></div>}
    </div>
  );
}

function PageHeader({ eyebrow, title, description, actions }: { eyebrow:string; title:string; description:string; actions?:React.ReactNode }) {
  return <section className="ca-page-header"><div><span className="ca-eyebrow"><Sparkles size={14}/>{eyebrow}</span><h1>{title}</h1><p>{description}</p></div>{actions && <div className="ca-page-actions">{actions}</div>}</section>;
}

function DashboardView({ user, company, onAdd, canManage }: { user:User; company?:Company; onAdd:()=>void; canManage:boolean }) {
  return <>
    <PageHeader eyebrow="Financial command center" title={`Bun venit, ${user.first_name}`} description={`Situația contabilă și fiscală pentru ${company?.name ?? 'compania ta'}.`} actions={<><button className="ca-button secondary" disabled={!canManage} onClick={onAdd}><Plus size={16}/>Companie</button><button className="ca-button primary"><Upload size={16}/>Încarcă document</button></>}/>
    <section className="ca-hero-grid"><article className="ca-ai-hero"><span className="ca-ai-kicker"><Bot size={16}/>Analiză AI locală</span><h2>Ai o imagine financiară clară, fără să cauți prin rapoarte.</h2><p>ContaAI combină regulile contabile cu analiza locală prin Ollama. Recomandările AI rămân propuneri și sunt validate de motorul contabil.</p><div className="ca-ai-summary"><div><CircleAlert size={18}/><span><strong>3 elemente</strong><small>necesită verificare</small></span></div><div><CheckCircle2 size={18}/><span><strong>96%</strong><small>reconciliere bancară</small></span></div><div><Gauge size={18}/><span><strong>94/100</strong><small>încredere fiscală</small></span></div></div><button className="ca-button light"><Sparkles size={16}/>Vezi analiza completă</button></article><article className="ca-score-card"><div className="ca-score"><span>97</span><small>/100</small></div><h3>Accounting Health</h3><p>Evidența contabilă este într-o stare foarte bună.</p><div className="ca-progress"><i style={{width:'97%'}}/></div><small>+2 față de luna trecută</small></article></section>
    <section className="ca-kpi-grid">{[
      ['Fiscal Confidence','94/100','Nivel ridicat de încredere',ShieldCheck],['Documente procesate','215','28 în această lună',FileText],['Alerte active','3','1 cu prioritate ridicată',CircleAlert],['Operațiuni AI','42','Analize locale finalizate',Activity]
    ].map(([label,value,desc,Icon]) => { const C = Icon as typeof ShieldCheck; return <article className="ca-kpi" key={String(label)}><span><C size={19}/></span><small>{String(label)}</small><strong>{String(value)}</strong><p>{String(desc)}</p></article>; })}</section>
    <section className="ca-two-col"><article className="ca-panel"><div className="ca-panel-header"><div><span>Priorități</span><h2>De rezolvat</h2></div><small>4 elemente</small></div>{['Încarcă factura Google Ads','Verifică cheltuielile de protocol','Atașează contractul Orange','Confirmă plata furnizorului Delta'].map((x,i)=><label className="ca-task" key={x}><input type="checkbox"/><span>{x}</span><small>{i===0?'Urgent':'Astăzi'}</small></label>)}</article><article className="ca-panel"><div className="ca-panel-header"><div><span>Activitate</span><h2>Ultimele operațiuni</h2></div></div>{['Factura Orange a fost procesată','Extrasul bancar a fost importat','Analiza fiscală a fost actualizată'].map((x,i)=><div className="ca-activity" key={x}><span>{i===0?<FileText size={17}/>:i===1?<Banknote size={17}/>:<ShieldCheck size={17}/>}</span><div><strong>{x}</strong><small>{i===0?'Acum 2 minute':i===1?'Acum 18 minute':'Astăzi, 20:46'}</small></div></div>)}</article></section>
  </>;
}

function WorkspaceView({ organization }: { organization?:Organization }) { return <><PageHeader eyebrow="Administrare" title="Workspace" description="Gestionează contextul organizației, rolul tău și companiile asociate."/><section className="ca-detail-grid"><article className="ca-panel ca-detail-card"><span className="ca-detail-icon"><Building2 size={21}/></span><small>Organizație activă</small><h2>{organization?.name ?? '—'}</h2><p>Un singur workspace poate grupa mai multe entități juridice și utilizatori.</p></article><article className="ca-panel ca-detail-card"><span className="ca-detail-icon"><ShieldCheck size={21}/></span><small>Rolul tău</small><h2>{organization?.role.name ?? '—'}</h2><p>Permisiunile sunt aplicate în backend și reflectate în interfață.</p></article><article className="ca-panel ca-detail-card"><span className="ca-detail-icon"><WalletCards size={21}/></span><small>Companii</small><h2>{organization?.companies.length ?? 0}</h2><p>Entități juridice configurate în workspace-ul curent.</p></article></section><article className="ca-panel ca-empty"><Sparkles size={24}/><h2>Workspace inteligent</h2><p>Aici vor fi adăugate setările generale, preferințele AI și regulile de lucru ale organizației.</p></article></> }

function CompaniesView({ companies, canManage, onAdd }: { companies:Company[]; canManage:boolean; onAdd:()=>void }) { return <><PageHeader eyebrow="Administrare" title="Companii" description="Entitățile juridice din workspace-ul activ." actions={<button className="ca-button primary" disabled={!canManage} onClick={onAdd}><Plus size={16}/>Adaugă companie</button>}/><section className="ca-company-grid">{companies.map(c=><article className="ca-company-card" key={c.id}><div className="ca-company-card-top"><span><Building2 size={20}/></span><small>{c.country_code}</small></div><h2>{c.name}</h2><p>{c.legal_form || 'Formă juridică nespecificată'}</p><div><span>CUI / CIF</span><strong>{c.tax_id || 'Nespecificat'}</strong></div></article>)}{!companies.length && <article className="ca-panel ca-empty"><Building2 size={24}/><h2>Nicio companie configurată</h2><p>Adaugă prima entitate juridică în acest workspace.</p></article>}</section></> }

function MembersView({ user, organization }: { user:User; organization?:Organization }) { return <><PageHeader eyebrow="Acces și permisiuni" title="Membri" description="Vizualizează cine are acces la workspace și ce rol deține." actions={<button className="ca-button primary" disabled><Plus size={16}/>Invită membru</button>}/><article className="ca-panel ca-members-table"><div className="ca-members-head"><span>Utilizator</span><span>Rol</span><span>Status</span></div><div className="ca-member-row"><div><span className="ca-avatar">{user.first_name.charAt(0)}{user.last_name.charAt(0)}</span><div><strong>{user.first_name} {user.last_name}</strong><small>{user.email}</small></div></div><span className="ca-role-pill">{organization?.role.name ?? 'Utilizator'}</span><span className="ca-status"><i/>Activ</span></div></article><div className="ca-note"><ShieldCheck size={18}/><div><strong>Invitațiile urmează în CAI-202.2</strong><p>Interfața este pregătită. Endpoint-urile pentru listarea și invitarea membrilor vor fi implementate în backend înainte de activarea butonului.</p></div></div></> }
