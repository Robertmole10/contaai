export type User = {
  first_name: string;
  last_name: string;
  email: string;
};

export type Company = {
  id: string;
  organization_id: string;
  name: string;
  tax_id: string | null;
  legal_form: string | null;
  country_code: string;
};

export type OrganizationRole = {
  key: string;
  name: string;
};

export type Organization = {
  id: string;
  name: string;
  role: OrganizationRole;
  companies: Company[];
};

export type Workspace = {
  organizations: Organization[];
};

export type ViewKey =
  | 'dashboard'
  | 'workspace'
  | 'companies'
  | 'members';
