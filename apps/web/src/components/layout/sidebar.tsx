'use client';

import {
  Bot,
  Building2,
  ChevronDown,
  HelpCircle,
  Settings,
  Sparkles,
  X,
} from 'lucide-react';

import { primaryNavigation, productNavigation } from './navigation';
import type { Organization, ViewKey } from '../../types/workspace';

type SidebarProps = {
  organizations: Organization[];
  activeOrganization?: Organization;
  activeView: ViewKey;
  mobileMenuOpen: boolean;
  onCloseMobile: () => void;
  onChangeOrganization: (organizationId: string) => void;
  onChangeView: (view: ViewKey) => void;
};

export function Sidebar({
  organizations,
  activeOrganization,
  activeView,
  mobileMenuOpen,
  onCloseMobile,
  onChangeOrganization,
  onChangeView,
}: SidebarProps) {
  return (
    <aside className={`ca-sidebar ${mobileMenuOpen ? 'is-open' : ''}`}>
      <div className="ca-sidebar-brand">
        <span>
          <Sparkles size={20} />
        </span>

        <div>
          <strong>ContaAI</strong>
          <small>Financial Intelligence Platform</small>
        </div>

        <button onClick={onCloseMobile} aria-label="Închide">
          <X size={19} />
        </button>
      </div>

      <div className="ca-sidebar-context">
        <label>Workspace</label>

        <div className="ca-select-shell">
          <Building2 size={16} />

          <select
            value={activeOrganization?.id ?? ''}
            onChange={(event) => onChangeOrganization(event.target.value)}
          >
            {organizations.map((organization) => (
              <option key={organization.id} value={organization.id}>
                {organization.name}
              </option>
            ))}
          </select>

          <ChevronDown size={15} />
        </div>

        <span className="ca-role-pill">
          {activeOrganization?.role.name ?? 'Utilizator'}
        </span>
      </div>

      <nav className="ca-sidebar-nav">
        <p>Administrare</p>

        {primaryNavigation.map((item) => {
          const Icon = item.icon;

          return (
            <button
              key={item.key}
              className={activeView === item.key ? 'active' : ''}
              onClick={() => {
                onChangeView(item.key);
                onCloseMobile();
              }}
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </button>
          );
        })}

        <p>Produse</p>

        {productNavigation.map((item) => {
          const Icon = item.icon;

          return (
            <button key={item.label}>
              <Icon size={18} />
              <span>{item.label}</span>
              {item.badge && <small>{item.badge}</small>}
            </button>
          );
        })}
      </nav>

      <div className="ca-sidebar-bottom">
        <button>
          <Settings size={18} />
          <span>Setări</span>
        </button>

        <button>
          <HelpCircle size={18} />
          <span>Ajutor</span>
        </button>

        <div className="ca-ai-status">
          <span>
            <Bot size={17} />
          </span>

          <div>
            <strong>AI Engine local</strong>
            <small>
              <i />
              Ollama · disponibil
            </small>
          </div>
        </div>
      </div>
    </aside>
  );
}
