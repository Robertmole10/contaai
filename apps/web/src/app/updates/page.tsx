import Link from 'next/link';

const versions = [
  {
    version: '0.2.0',
    date: 'Sprint 2',
    title: 'Multi-tenancy și ERP Workspace',
    status: 'Versiune stabilă',
    highlights: [
      'Organizații și companii multiple',
      'Roluri și permisiuni RBAC',
      'Company switcher și onboarding',
      'Dashboard ERP și sidebar modular',
      'API-uri pentru workspace, organizații și companii'
    ]
  },
  {
    version: '0.1.0',
    date: 'Sprint 1',
    title: 'Authentication & Identity',
    status: 'Versiune stabilă',
    highlights: [
      'Înregistrare, login și logout',
      'JWT access și refresh tokens',
      'Parole securizate cu Argon2',
      'Dashboard inițial',
      'Fundație Docker, FastAPI, Next.js și Alembic'
    ]
  }
];

const upcoming = [
  'Document Inbox cu upload PDF, JPG și PNG',
  'Stocare securizată în MinIO',
  'Procesare asincronă prin Redis și worker',
  'Pregătire pentru OCR și extracție AI'
];

export default function UpdatesPage() {
  return <main className="updates-page">
    <div className="updates-wrap">
      <header className="updates-hero">
        <div>
          <span className="updates-kicker">CONTAAI PRODUCT UPDATES</span>
          <h1>Evoluția platformei</h1>
          <p>Toate funcționalitățile, îmbunătățirile și schimbările importante, de la prima versiune până la cea mai recentă.</p>
        </div>
        <Link href="/dashboard" className="button-link">Înapoi la aplicație</Link>
      </header>

      <section className="updates-summary">
        <article><strong>2</strong><span>versiuni stabile</span></article>
        <article><strong>10+</strong><span>funcționalități livrate</span></article>
        <article><strong>3</strong><span>module în dezvoltare</span></article>
      </section>

      <section className="release-section">
        <div className="release-heading">
          <span className="release-dot current" />
          <div><small>ÎN DEZVOLTARE</small><h2>Versiunea 0.3.0 — Document Inbox</h2></div>
        </div>
        <div className="release-card upcoming-card">
          <p>Sprintul curent introduce fundația pentru colectarea și procesarea documentelor contabile.</p>
          <ul>{upcoming.map(item => <li key={item}>{item}</li>)}</ul>
        </div>
      </section>

      {versions.map((release) => <section className="release-section" key={release.version}>
        <div className="release-heading">
          <span className="release-dot" />
          <div><small>{release.date.toUpperCase()}</small><h2>Versiunea {release.version} — {release.title}</h2></div>
          <span className="release-status">{release.status}</span>
        </div>
        <div className="release-card">
          <ul>{release.highlights.map(item => <li key={item}>{item}</li>)}</ul>
        </div>
      </section>)}

      <footer className="updates-footer">
        <strong>ContaAI</strong>
        <p>Istoricul complet este actualizat la fiecare versiune publicată.</p>
      </footer>
    </div>
  </main>;
}
