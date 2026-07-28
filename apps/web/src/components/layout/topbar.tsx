'use client';

import {
  Bell,
  Building2,
  ChevronDown,
  LogOut,
  Menu,
  Search,
  Sparkles,
} from 'lucide-react';

import { ThemeToggle } from '../theme-toggle';
import type { Company, Organization, User } from '../../types/workspace';

type TopbarProps = {
  user: User;
  activeOrganization?: Organization;
  companies: Company[];
  activeCompany?: Company;
  onOpenMobileMenu: () => void;
  onChangeCompany: (companyId: string) => void;
  onLogout: () => void;
};

export function Topbar({
  user,
  activeOrganization,
  companies,
  activeCompany,
  onOpenMobileMenu,
  onChangeCompany,
  onLogout,
}: TopbarProps) {
  const initials = `${user.first_name.charAt(0)}${user.last_name.charAt(0)}`;

  return (
    <header className="ca-topbar">
      <div className="ca-topbar-left">
        <button className="ca-mobile-menu" onClick={onOpenMobileMenu}>
          <Menu size={20} />
        </button>

        <div className="ca-company-switcher">
          <label>Companie activă</label>

          <div className="ca-select-shell">
            <Building2 size={16} />

            <select
              value={activeCompany?.id ?? ''}
              onChange={(event) => onChangeCompany(event.target.value)}
              disabled={!companies.length}
            >
              {!companies.length && <option>Nicio companie</option>}

              {companies.map((company) => (
                <option key={company.id} value={company.id}>
                  {company.name}
                </option>
              ))}
            </select>

            <ChevronDown size={15} />
          </div>
        </div>
      </div>

      <div className="ca-topbar-actions">
        <button className="ca-search">
          <Search size={17} />
          <span>Caută</span>
          <kbd>⌘ K</kbd>
        </button>

        <button className="ca-ai-button">
          <Sparkles size={16} />
          Întreabă ContaAI
        </button>

        <ThemeToggle />

        <button className="ca-icon-button">
          <Bell size={18} />
        </button>

        <div className="ca-user">
          <span>{initials}</span>

          <div>
            <strong>
              {user.first_name} {user.last_name}
            </strong>

            <small>{activeOrganization?.role.name ?? 'Utilizator'}</small>
          </div>
        </div>

        <button className="ca-icon-button" onClick={onLogout}>
          <LogOut size={18} />
        </button>
      </div>
    </header>
  );
}
