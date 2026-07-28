import {
  Banknote,
  BookOpen,
  Bot,
  Building2,
  FileText,
  LayoutDashboard,
  ReceiptText,
  ShieldCheck,
  TrendingUp,
  Users,
  WalletCards,
} from 'lucide-react';

import type { ViewKey } from '../../types/workspace';

export const primaryNavigation = [
  { key: 'dashboard' as ViewKey, label: 'Dashboard', icon: LayoutDashboard },
  { key: 'workspace' as ViewKey, label: 'Workspace', icon: Building2 },
  { key: 'companies' as ViewKey, label: 'Companii', icon: WalletCards },
  { key: 'members' as ViewKey, label: 'Membri', icon: Users },
];

export const productNavigation = [
  { label: 'Documente', icon: FileText, badge: '12' },
  { label: 'Bancă', icon: Banknote, badge: '3' },
  { label: 'Facturi', icon: ReceiptText },
  { label: 'Contabilitate', icon: BookOpen },
  { label: 'Fiscal Intelligence', icon: ShieldCheck, badge: 'Nou' },
  { label: 'Asistent AI', icon: Bot },
  { label: 'Rapoarte', icon: TrendingUp },
];
