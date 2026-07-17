'use client';

import {
  ChangeEvent,
  FormEvent,
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
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

type UploadedDocument = {
  id: string;
  company_id: string;
  uploaded_by_id: string;
  original_filename: string;
  mime_type: string;
  extension: string;
  file_size: number;
  checksum_sha256: string;
  document_type: string;
  status: string;
  ai_confidence: string | number | null;
  processing_error: string | null;
  created_at: string;
  updated_at: string;
};

const modules = [
  ['⌂', 'Dashboard'],
  ['▤', 'Documente'],
  ['↗', 'Facturi'],
  ['≡', 'Contabilitate'],
  ['%', 'TVA'],
  ['▥', 'Rapoarte'],
  ['⚙', 'Setări'],
];

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? 'https://api-conta.bmobile.ro';

export default function DashboardPage() {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const [user, setUser] = useState<User | null>(null);
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [activeCompanyId, setActiveCompanyId] = useState('');
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [showAddCompany, setShowAddCompany] = useState(false);

  const [error, setError] = useState('');
  const [uploadError, setUploadError] = useState('');
  const [uploadSuccess, setUploadSuccess] = useState('');
  const [isUploading, setIsUploading] = useState(false);

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
          await apiFetch('/auth/refresh', {
            method: 'POST',
          });

          const currentUser = await apiFetch<User>('/auth/me');

          setUser(currentUser);
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
    companies.find(company => company.id === activeCompanyId) ?? companies[0];

  const activeOrganization =
    workspace?.organizations.find(
      organization => organization.id === activeCompany?.organization_id,
    ) ?? workspace?.organizations[0];

  function openDocumentPicker() {
    setUploadError('');
    setUploadSuccess('');

    if (!activeCompany?.id) {
      setUploadError(
        'Trebuie să adaugi sau să selectezi o companie înainte de încărcarea documentului.',
      );
      return;
    }

    fileInputRef.current?.click();
  }

  async function handleDocumentUpload(
    event: ChangeEvent<HTMLInputElement>,
  ) {
    const input = event.currentTarget;
    const file = input.files?.[0];

    if (!file) {
      return;
    }

    if (!activeCompany?.id) {
      setUploadError(
        'Trebuie să selectezi o companie înainte de încărcarea documentului.',
      );
      input.value = '';
      return;
    }

    setIsUploading(true);
    setUploadError('');
    setUploadSuccess('');

    try {
      const formData = new FormData();
      formData.append('file', file);

      const endpoint =
        `${API_URL}/companies/${activeCompany.id}/documents` +
        '?document_type=purchase_invoice';

      const response = await fetch(endpoint, {
        method: 'POST',
        credentials: 'include',
        headers: {
          Accept: 'application/json',
        },
        body: formData,
      });

      const payload = (await response
        .json()
        .catch(() => null)) as UploadedDocument | { detail?: string } | null;

      if (!response.ok) {
        const detail =
          payload && 'detail' in payload
            ? payload.detail
            : 'Încărcarea documentului a eșuat.';

        throw new Error(detail || 'Încărcarea documentului a eșuat.');
      }

      const document = payload as UploadedDocument;

      setUploadSuccess(
        `Documentul „${document.original_filename}” a fost încărcat cu succes.`,
      );
    } catch (uploadException) {
      setUploadError(
        uploadException instanceof Error
          ? uploadException.message
          : 'Încărcarea documentului a eșuat.',
      );
    } finally {
      setIsUploading(false);
      input.value = '';
    }
  }

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
    } catch (exception) {
      setError(
        exception instanceof Error
          ? exception.message
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
    } catch (exception) {
      setError(
        exception instanceof Error
          ? exception.message
          : 'A apărut o eroare.',
      );
    }
  }

  async function logout() {
    await apiFetch('/auth/logout', {
      method: 'POST',
    });

    router.replace('/login');
  }

  if (!user || !workspace) {
    return (
      <main className="auth-shell">
        <p>Se pregătește workspace-ul…</p>
      </main>
    );
  }

  return (
    <div className="erp-shell">
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.png,.jpg,.jpeg,application/pdf,image/png,image/jpeg"
        hidden
        onChange={handleDocumentUpload}
      />

      <aside className="sidebar">
        <div className="logo-mark">
          <span>CA</span>
          <strong>ContaAI</strong>
        </div>

        <nav>
          {modules.map(([icon, label], index) => (
            <button
              key={label}
              type="button"
              className={index === 0 ? 'nav-item active' : 'nav-item'}
            >
              <span>{icon}</span>
              {label}
            </button>
          ))}

          <Link href="/updates" className="nav-item-link">
            <span>◴</span>
            Actualizări
          </Link>
        </nav>

        <div className="sidebar-bottom">
          <div className="ai-status">
            <span className="pulse" />

            <div>
              <strong>AI Engine</strong>
              <small>Pregătit pentru documente</small>
            </div>
          </div>
        </div>
      </aside>

      <div className="erp-main">
        <header className="topbar">
          <div className="company-switcher">
            <label>Companie activă</label>

            <select
              value={activeCompany?.id ?? ''}
              onChange={event => {
                setActiveCompanyId(event.target.value);
                setUploadError('');
                setUploadSuccess('');
              }}
              disabled={!companies.length}
            >
              {!companies.length && (
                <option value="">Nicio companie</option>
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

          <div className="top-actions">
            <button type="button" className="icon-button">
              ⌕
            </button>

            <button type="button" className="icon-button">
              ◔
            </button>

            <div className="user-chip">
              <span>
                {user.first_name[0]}
                {user.last_name[0]}
              </span>

              <div>
                <strong>
                  {user.first_name} {user.last_name}
                </strong>

                <small>
                  {activeOrganization?.role.name ?? 'Utilizator'}
                </small>
              </div>
            </div>

            <button
              type="button"
              className="ghost-button"
              onClick={logout}
            >
              Ieșire
            </button>
          </div>
        </header>

        <main className="content-area">
          <div className="page-heading">
            <div>
              <p className="eyebrow-text">PREZENTARE GENERALĂ</p>
              <h1>Bun venit, {user.first_name}</h1>
              <p>
                Ai control asupra activității contabile dintr-un singur
                loc.
              </p>
            </div>

            <div className="heading-actions">
              <button
                type="button"
                className="secondary"
                onClick={() => {
                  setError('');
                  setShowAddCompany(true);
                }}
              >
                + Companie
              </button>

              <button
                type="button"
                onClick={openDocumentPicker}
                disabled={isUploading || !activeCompany}
              >
                {isUploading
                  ? 'Se încarcă…'
                  : '+ Încarcă document'}
              </button>
            </div>
          </div>

          {uploadError && (
            <p className="error" role="alert">
              {uploadError}
            </p>
          )}

          {uploadSuccess && (
            <p className="success" role="status">
              {uploadSuccess}
            </p>
          )}

          <section className="metric-grid">
            <article>
              <div>
                <small>Documente luna aceasta</small>
                <strong>0</strong>
                <span>În așteptarea primului import</span>
              </div>
              <i>▤</i>
            </article>

            <article>
              <div>
                <small>De procesat</small>
                <strong>0</strong>
                <span>Inbox-ul este curat</span>
              </div>
              <i>✓</i>
            </article>

            <article>
              <div>
                <small>TVA estimat</small>
                <strong>0 lei</strong>
                <span>Perioada curentă</span>
              </div>
              <i>%</i>
            </article>

            <article>
              <div>
                <small>Companii active</small>
                <strong>{companies.length}</strong>
                <span>
                  {workspace.organizations.length} organizații
                </span>
              </div>
              <i>▦</i>
            </article>
          </section>

          <section className="dashboard-grid">
            <article className="panel activity-panel">
              <div className="panel-title">
                <div>
                  <h2>Activitate recentă</h2>
                  <p>Ultimele acțiuni din workspace</p>
                </div>

                <button type="button" className="link-button">
                  Vezi tot
                </button>
              </div>

              <div className="empty-state">
                <div>↥</div>
                <h3>Încarcă primul document</h3>
                <p>
                  Folosește butonul „Încarcă document” din partea de
                  sus.
                </p>
              </div>
            </article>

            <article className="panel quick-panel">
              <div className="panel-title">
                <div>
                  <h2>Acțiuni rapide</h2>
                  <p>Continuă configurarea ContaAI</p>
                </div>
              </div>

              <button
                type="button"
                onClick={() => {
                  setError('');
                  setShowAddCompany(true);
                }}
              >
                <span>▦</span>

                <div>
                  <strong>Adaugă o companie</strong>
                  <small>Creează un nou dosar contabil</small>
                </div>

                <b>›</b>
              </button>

              <button
                type="button"
                onClick={openDocumentPicker}
                disabled={isUploading || !activeCompany}
              >
                <span>⇧</span>

                <div>
                  <strong>
                    {isUploading
                      ? 'Se încarcă documentul…'
                      : 'Importă documente'}
                  </strong>
                  <small>PDF, PNG, JPG sau JPEG</small>
                </div>

                <b>›</b>
              </button>

              <button type="button">
                <span>⚙</span>

                <div>
                  <strong>Configurează contabilitatea</strong>
                  <small>Plan de conturi și perioade</small>
                </div>

                <b>›</b>
              </button>
            </article>
          </section>
        </main>
      </div>

      {(showOnboarding || showAddCompany) && (
        <div className="modal-backdrop">
          <div className="modal-card">
            <div className="modal-head">
              <div>
                <span className="eyebrow-text">
                  {showOnboarding
                    ? 'CONFIGURARE INIȚIALĂ'
                    : 'COMPANIE NOUĂ'}
                </span>

                <h2>
                  {showOnboarding
                    ? 'Creează workspace-ul tău'
                    : 'Adaugă o companie'}
                </h2>

                <p>
                  {showOnboarding
                    ? 'Configurează organizația și prima companie.'
                    : `Compania va fi adăugată în ${activeOrganization?.name}.`}
                </p>
              </div>

              {!showOnboarding && (
                <button
                  type="button"
                  className="modal-close"
                  onClick={() => {
                    setError('');
                    setShowAddCompany(false);
                  }}
                >
                  ×
                </button>
              )}
            </div>

            <form
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

              <div className="two-cols">
                <label>
                  CUI / CIF
                  <input
                    name="taxId"
                    placeholder="RO12345678"
                  />
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

              {error && <p className="error">{error}</p>}

              <button type="submit">
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