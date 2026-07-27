'use client';

import { FormEvent, useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import {
  Activity,
  ArrowRight,
  BadgeCheck,
  Banknote,
  Bell,
  BookOpen,
  Bot,
  Building2,
  CheckCircle2,
  ChevronRight,
  CircleAlert,
  FileCheck2,
  FileText,
  Gauge,
  HelpCircle,
  LayoutDashboard,
  LogOut,
  Menu,
  Plus,
  ReceiptText,
  Search,
  Settings,
  ShieldCheck,
  Sparkles,
  TrendingUp,
  Upload,
  WalletCards,
  X,
} from 'lucide-react';

import { ThemeToggle } from '../../components/theme-toggle';
import { apiFetch } from '../../lib/api';

type User = {
  first_name: string;
  last_name: string;
  email: string;
};

type Company = {
  id: string;
  organization_id: string;
  name: string;
  tax_id: string | null;
  legal_form: string | null;
  country_code: string;
};

type Organization = {
  id: string;
  name: string;
  role: {
    key: string;
    name: string;
  };
  companies: Company[];
};

type Workspace = {
  organizations: Organization[];
};

const navigation = [
  { label: 'Dashboard', icon: LayoutDashboard, active: true },
  { label: 'Documente', icon: FileText, badge: '12' },
  { label: 'Bancă', icon: WalletCards, badge: '3' },
  { label: 'Facturi', icon: ReceiptText },
  { label: 'Contabilitate', icon: BookOpen },
  { label: 'Fiscal Intelligence', icon: ShieldCheck, badge: 'Nou' },
  { label: 'Asistent AI', icon: Bot },
  { label: 'Rapoarte', icon: TrendingUp },
];

const fiscalAlerts = [
  {
    title: '3 cheltuieli fără document justificativ',
    description: 'Plățile bancare nu au fost asociate unor facturi sau bonuri.',
    status: 'danger',
    icon: CircleAlert,
  },
  {
    title: 'Protocol aproape de plafon',
    description: 'Consumul estimat a ajuns la 86% din limita configurată.',
    status: 'warning',
    icon: Gauge,
  },
  {
    title: 'Reconciliere bancară 96%',
    description: 'Majoritatea tranzacțiilor au fost asociate automat.',
    status: 'success',
    icon: CheckCircle2,
  },
];

const recentActivity = [
  {
    title: 'Factura Orange a fost procesată',
    description: 'OCR finalizat și furnizor identificat.',
    time: 'Acum 2 minute',
    icon: FileCheck2,
  },
  {
    title: 'Extrasul bancar a fost importat',
    description: '42 de tranzacții detectate.',
    time: 'Acum 18 minute',
    icon: Banknote,
  },
  {
    title: 'Analiza fiscală a fost actualizată',
    description: 'Scorul de conformitate a crescut cu 3 puncte.',
    time: 'Astăzi, 20:46',
    icon: ShieldCheck,
  },
];

export default function DashboardPage() {
  const router = useRouter();

  const [user, setUser] = useState<User | null>(null);
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [activeCompanyId, setActiveCompanyId] = useState('');
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [showAddCompany, setShowAddCompany] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [error, setError] = useState('');

  async function loadWorkspace() {
    const data = await apiFetch<Workspace>('/workspace');
    setWorkspace(data);

    if (!data.organizations.length) {
      setShowOnboarding(true);
    }

    const firstCompany = data.organizations.flatMap(
      organization => organization.companies,
    )[0];

    if (firstCompany && !activeCompanyId) {
      setActiveCompanyId(firstCompany.id);
    }
  }

  useEffect(() => {
    apiFetch<User>('/auth/me')
      .then(async currentUser => {
        setUser(currentUser);
        await loadWorkspace();
      })
      .catch(async () => {
        try {
          await apiFetch('/auth/refresh', { method: 'POST' });
          setUser(await apiFetch<User>('/auth/me'));
          await loadWorkspace();
        } catch {
          router.replace('/login');
        }
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [router]);

  const companies = useMemo(
    () =>
      workspace?.organizations.flatMap(
        organization => organization.companies,
      ) ?? [],
    [workspace],
  );

  const activeCompany =
    companies.find(company => company.id === activeCompanyId) ??
    companies[0];

  const activeOrganization =
    workspace?.organizations.find(
      organization => organization.id === activeCompany?.organization_id,
    ) ?? workspace?.organizations[0];

  async function createOrganization(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();
    setError('');

    const form = new FormData(event.currentTarget);

    try {
      await apiFetch('/organizations', {
        method: 'POST',
        body: JSON.stringify({
          name: form.get('organizationName'),
          company: {
            name: form.get('companyName'),
            tax_id: form.get('taxId') || null,
            legal_form: form.get('legalForm') || null,
            country_code: 'RO',
          },
        }),
      });

      setShowOnboarding(false);
      await loadWorkspace();
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : 'A apărut o eroare.',
      );
    }
  }

  async function addCompany(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError('');

    if (!activeOrganization) {
      return;
    }

    const form = new FormData(event.currentTarget);

    try {
      const company = await apiFetch<Company>(
        `/organizations/${activeOrganization.id}/companies`,
        {
          method: 'POST',
          body: JSON.stringify({
            name: form.get('companyName'),
            tax_id: form.get('taxId') || null,
            legal_form: form.get('legalForm') || null,
            country_code: 'RO',
          }),
        },
      );

      setShowAddCompany(false);
      await loadWorkspace();
      setActiveCompanyId(company.id);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : 'A apărut o eroare.',
      );
    }
  }

  async function logout() {
    await apiFetch('/auth/logout', { method: 'POST' });
    router.replace('/login');
  }

  if (!user || !workspace) {
    return (
      <main className="workspace-loading">
        <div className="loading-logo">CA</div>
        <p>Se pregătește workspace-ul ContaAI…</p>
      </main>
    );
  }

  const initials = `${user.first_name.charAt(0)}${user.last_name.charAt(0)}`;

  return (
    <div className="app-shell">
      <aside
        className={`app-sidebar ${mobileMenuOpen ? 'mobile-open' : ''}`}
      >
        <div className="sidebar-header">
          <div className="brand-lockup">
            <div className="brand-symbol">
              <Sparkles size={19} />
            </div>

            <div>
              <strong>ContaAI</strong>
              <span>Tax & Accounting Copilot</span>
            </div>
          </div>

          <button
            className="mobile-sidebar-close"
            type="button"
            onClick={() => setMobileMenuOpen(false)}
            aria-label="Închide meniul"
          >
            <X size={20} />
          </button>
        </div>

        <div className="sidebar-section-label">Workspace</div>

        <nav className="sidebar-navigation">
          {navigation.map(item => {
            const Icon = item.icon;

            return (
              <button
                className={`sidebar-link ${item.active ? 'active' : ''}`}
                type="button"
                key={item.label}
              >
                <Icon size={19} strokeWidth={1.9} />
                <span>{item.label}</span>

                {item.badge && (
                  <small className="navigation-badge">{item.badge}</small>
                )}
              </button>
            );
          })}
        </nav>

        <div className="sidebar-footer">
          <button className="sidebar-link" type="button">
            <Settings size={19} />
            <span>Setări</span>
          </button>

          <button className="sidebar-link" type="button">
            <HelpCircle size={19} />
            <span>Ajutor și suport</span>
          </button>

          <div className="engine-status">
            <div className="engine-status-icon">
              <Bot size={18} />
            </div>

            <div>
              <strong>AI Engine</strong>
              <span>
                <i />
                Operațional
              </span>
            </div>
          </div>
        </div>
      </aside>

      {mobileMenuOpen && (
        <button
          className="mobile-overlay"
          type="button"
          aria-label="Închide meniul"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      <div className="app-main">
        <header className="app-topbar">
          <div className="topbar-left">
            <button
              className="mobile-menu-button"
              type="button"
              onClick={() => setMobileMenuOpen(true)}
              aria-label="Deschide meniul"
            >
              <Menu size={21} />
            </button>

            <div className="company-selector">
              <span>Companie activă</span>

              <div className="company-selector-control">
                <Building2 size={17} />

                <select
                  value={activeCompany?.id ?? ''}
                  onChange={event =>
                    setActiveCompanyId(event.target.value)
                  }
                  disabled={!companies.length}
                >
                  {!companies.length && (
                    <option>Nicio companie</option>
                  )}

                  {workspace.organizations.map(organization => (
                    <optgroup
                      key={organization.id}
                      label={organization.name}
                    >
                      {organization.companies.map(company => (
                        <option key={company.id} value={company.id}>
                          {company.name}
                        </option>
                      ))}
                    </optgroup>
                  ))}
                </select>
              </div>
            </div>
          </div>

          <div className="topbar-actions">
            <button
              className="search-button"
              type="button"
              aria-label="Caută"
            >
              <Search size={18} />
              <span>Caută</span>
              <kbd>⌘ K</kbd>
            </button>

            <button
              className="ask-ai-button"
              type="button"
            >
              <Sparkles size={17} />
              <span>Întreabă ContaAI</span>
            </button>

            <ThemeToggle />

            <button
              className="icon-button notification-button"
              type="button"
              aria-label="Notificări"
            >
              <Bell size={19} />
              <span />
            </button>

            <div className="topbar-divider" />

            <div className="user-menu">
              <div className="user-avatar">{initials}</div>

              <div className="user-details">
                <strong>
                  {user.first_name} {user.last_name}
                </strong>
                <span>
                  {activeOrganization?.role.name ?? 'Utilizator'}
                </span>
              </div>
            </div>

            <button
              className="icon-button"
              type="button"
              onClick={logout}
              title="Ieșire"
              aria-label="Ieșire"
            >
              <LogOut size={18} />
            </button>
          </div>
        </header>

        <main className="dashboard-content">
          <section className="dashboard-heading">
            <div>
              <div className="page-eyebrow">
                <BadgeCheck size={15} />
                Prezentare generală
              </div>

              <h1>Bun venit, {user.first_name}</h1>

              <p>
                Situația contabilă și fiscală pentru{' '}
                <strong>{activeCompany?.name ?? 'compania ta'}</strong>.
              </p>
            </div>

            <div className="heading-actions">
              <button
                className="button secondary-button"
                type="button"
                onClick={() => setShowAddCompany(true)}
              >
                <Plus size={17} />
                Companie
              </button>

              <button className="button primary-button" type="button">
                <Upload size={17} />
                Încarcă document
              </button>
            </div>
          </section>

          <motion.section
            className="kpi-grid"
            initial="hidden"
            animate="visible"
            variants={{
              hidden: {},
              visible: {
                transition: {
                  staggerChildren: 0.07,
                },
              },
            }}
          >
            <KpiCard
              label="Accounting Health"
              value="97"
              suffix="/100"
              description="Evidență contabilă sănătoasă"
              trend="+2 față de luna trecută"
              icon={Activity}
              tone="success"
            />

            <KpiCard
              label="Fiscal Confidence"
              value="94"
              suffix="/100"
              description="Nivel ridicat de încredere"
              trend="3 verificări necesare"
              icon={ShieldCheck}
              tone="primary"
            />

            <KpiCard
              label="Documente procesate"
              value="215"
              description="În perioada curentă"
              trend="+28 în această lună"
              icon={FileText}
              tone="neutral"
            />

            <KpiCard
              label="Alerte active"
              value="3"
              description="Necesită atenția ta"
              trend="1 alertă cu prioritate ridicată"
              icon={CircleAlert}
              tone="danger"
            />
          </motion.section>

          <section className="main-dashboard-grid">
            <article className="dashboard-panel fiscal-panel">
              <div className="panel-header">
                <div>
                  <span className="panel-kicker">
                    <Sparkles size={15} />
                    Fiscal Intelligence
                  </span>

                  <h2>Analiză și recomandări AI</h2>

                  <p>
                    ContaAI urmărește automat riscurile și documentele
                    lipsă.
                  </p>
                </div>

                <button className="text-button" type="button">
                  Vezi toate
                  <ArrowRight size={16} />
                </button>
              </div>

              <div className="fiscal-score-row">
                <div className="score-ring">
                  <svg viewBox="0 0 120 120" role="img">
                    <circle
                      className="score-ring-track"
                      cx="60"
                      cy="60"
                      r="50"
                    />
                    <circle
                      className="score-ring-progress"
                      cx="60"
                      cy="60"
                      r="50"
                      pathLength="100"
                    />
                  </svg>

                  <div className="score-ring-value">
                    <strong>94</strong>
                    <span>/100</span>
                  </div>
                </div>

                <div className="score-explanation">
                  <div className="score-status">
                    <CheckCircle2 size={18} />
                    Nivel ridicat de încredere fiscală
                  </div>

                  <p>
                    Datele sunt în general complete. Trei elemente
                    necesită verificare înainte de închiderea perioadei.
                  </p>

                  <div className="score-meta">
                    <span>
                      <b>96%</b>
                      Reconciliere
                    </span>
                    <span>
                      <b>98%</b>
                      Documente
                    </span>
                    <span>
                      <b>89%</b>
                      Context fiscal
                    </span>
                  </div>
                </div>
              </div>

              <div className="insight-list">
                {fiscalAlerts.map(alert => {
                  const Icon = alert.icon;

                  return (
                    <button
                      className="insight-row"
                      type="button"
                      key={alert.title}
                    >
                      <span
                        className={`insight-icon ${alert.status}`}
                      >
                        <Icon size={18} />
                      </span>

                      <span className="insight-copy">
                        <strong>{alert.title}</strong>
                        <small>{alert.description}</small>
                      </span>

                      <ChevronRight size={18} />
                    </button>
                  );
                })}
              </div>
            </article>

            <article className="dashboard-panel quick-actions-panel">
              <div className="panel-header compact">
                <div>
                  <h2>Acțiuni rapide</h2>
                  <p>Continuă activitatea curentă.</p>
                </div>
              </div>

              <div className="quick-action-list">
                <QuickAction
                  icon={Upload}
                  title="Încarcă document"
                  description="Factură, bon sau contract"
                />

                <QuickAction
                  icon={Banknote}
                  title="Importă extras bancar"
                  description="CSV, XLSX sau PDF"
                />

                <QuickAction
                  icon={Bot}
                  title="Întreabă ContaAI"
                  description="Asistență contabilă și fiscală"
                />

                <QuickAction
                  icon={ShieldCheck}
                  title="Rulează audit fiscal"
                  description="Simulare preliminară de control"
                />

                <QuickAction
                  icon={Building2}
                  title="Adaugă o companie"
                  description="Configurează un nou dosar"
                  onClick={() => setShowAddCompany(true)}
                />
              </div>
            </article>
          </section>

          <section className="secondary-dashboard-grid">
            <article className="dashboard-panel activity-panel">
              <div className="panel-header compact">
                <div>
                  <h2>Activitate recentă</h2>
                  <p>Ultimele operațiuni din workspace.</p>
                </div>

                <button className="text-button" type="button">
                  Vezi istoricul
                </button>
              </div>

              <div className="activity-timeline">
                {recentActivity.map((item, index) => {
                  const Icon = item.icon;

                  return (
                    <div className="activity-entry" key={item.title}>
                      <div className="activity-marker">
                        <span>
                          <Icon size={17} />
                        </span>

                        {index < recentActivity.length - 1 && <i />}
                      </div>

                      <div className="activity-copy">
                        <strong>{item.title}</strong>
                        <p>{item.description}</p>
                      </div>

                      <time>{item.time}</time>
                    </div>
                  );
                })}
              </div>
            </article>

            <article className="dashboard-panel tasks-panel">
              <div className="panel-header compact">
                <div>
                  <h2>De rezolvat</h2>
                  <p>Elemente care necesită intervenție.</p>
                </div>

                <span className="task-count">4</span>
              </div>

              <div className="task-list">
                {[
                  'Încarcă factura Google Ads',
                  'Verifică cheltuielile de protocol',
                  'Atașează contractul Orange',
                  'Confirmă plata furnizorului Delta',
                ].map((task, index) => (
                  <label className="task-row" key={task}>
                    <input type="checkbox" />
                    <span>{task}</span>
                    <small>{index === 0 ? 'Urgent' : 'Astăzi'}</small>
                  </label>
                ))}
              </div>
            </article>
          </section>
        </main>
      </div>

      {(showOnboarding || showAddCompany) && (
        <div className="modal-backdrop">
          <div className="modal-card">
            <div className="modal-header">
              <div>
                <span className="modal-eyebrow">
                  {showOnboarding
                    ? 'Configurare inițială'
                    : 'Companie nouă'}
                </span>

                <h2>
                  {showOnboarding
                    ? 'Creează workspace-ul tău'
                    : 'Adaugă o companie'}
                </h2>

                <p>
                  {showOnboarding
                    ? 'Configurează organizația și prima companie.'
                    : `Compania va fi adăugată în ${
                        activeOrganization?.name ?? 'organizația activă'
                      }.`}
                </p>
              </div>

              {!showOnboarding && (
                <button
                  className="icon-button"
                  type="button"
                  onClick={() => setShowAddCompany(false)}
                  aria-label="Închide"
                >
                  <X size={20} />
                </button>
              )}
            </div>

            <form
              className="company-form"
              onSubmit={
                showOnboarding ? createOrganization : addCompany
              }
            >
              {showOnboarding && (
                <label>
                  Numele organizației
                  <input
                    name="organizationName"
                    placeholder="Ex: Cabinet Robert Mole"
                    required
                    minLength={2}
                  />
                </label>
              )}

              <label>
                Numele companiei
                <input
                  name="companyName"
                  placeholder="Ex: Demo Consulting SRL"
                  required
                  minLength={2}
                />
              </label>

              <div className="form-grid">
                <label>
                  CUI / CIF
                  <input name="taxId" placeholder="RO12345678" />
                </label>

                <label>
                  Forma juridică
                  <select name="legalForm">
                    <option value="SRL">SRL</option>
                    <option value="PFA">PFA</option>
                    <option value="CMI">Cabinet medical</option>
                    <option value="SA">SA</option>
                    <option value="">Alta</option>
                  </select>
                </label>
              </div>

              {error && <p className="form-error">{error}</p>}

              <button
                className="button primary-button full-width"
                type="submit"
              >
                {showOnboarding
                  ? 'Creează workspace-ul'
                  : 'Adaugă compania'}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

type IconComponent = React.ComponentType<{
  size?: number;
  strokeWidth?: number;
}>;

function KpiCard({
  label,
  value,
  suffix,
  description,
  trend,
  icon: Icon,
  tone,
}: {
  label: string;
  value: string;
  suffix?: string;
  description: string;
  trend: string;
  icon: IconComponent;
  tone: 'success' | 'primary' | 'neutral' | 'danger';
}) {
  return (
    <motion.article
      className={`kpi-card ${tone}`}
      variants={{
        hidden: { opacity: 0, y: 14 },
        visible: { opacity: 1, y: 0 },
      }}
      transition={{ duration: 0.35, ease: 'easeOut' }}
      whileHover={{ y: -3 }}
    >
      <div className="kpi-card-top">
        <span className="kpi-label">{label}</span>

        <span className="kpi-icon">
          <Icon size={20} strokeWidth={1.9} />
        </span>
      </div>

      <div className="kpi-value">
        {value}
        {suffix && <small>{suffix}</small>}
      </div>

      <p>{description}</p>

      <div className="kpi-trend">{trend}</div>
    </motion.article>
  );
}

function QuickAction({
  icon: Icon,
  title,
  description,
  onClick,
}: {
  icon: IconComponent;
  title: string;
  description: string;
  onClick?: () => void;
}) {
  return (
    <button
      className="quick-action"
      type="button"
      onClick={onClick}
    >
      <span className="quick-action-icon">
        <Icon size={19} />
      </span>

      <span>
        <strong>{title}</strong>
        <small>{description}</small>
      </span>

      <ChevronRight size={18} />
    </button>
  );
}
