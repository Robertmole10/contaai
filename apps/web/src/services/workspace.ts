import { apiFetch } from '../lib/api';
import type {
  Company,
  Workspace,
} from '../types/workspace';

export type CreateOrganizationInput = {
  name: string;
  company: {
    name: string;
    tax_id: string | null;
    legal_form: string | null;
    country_code: string;
  };
};

export type CreateCompanyInput = {
  name: string;
  tax_id: string | null;
  legal_form: string | null;
  country_code: string;
};

export const workspaceService = {
  getWorkspace(): Promise<Workspace> {
    return apiFetch<Workspace>('/workspace');
  },

  createOrganization(
    payload: CreateOrganizationInput,
  ): Promise<void> {
    return apiFetch<void>('/organizations', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  createCompany(
    organizationId: string,
    payload: CreateCompanyInput,
  ): Promise<Company> {
    return apiFetch<Company>(
      `/organizations/${organizationId}/companies`,
      {
        method: 'POST',
        body: JSON.stringify(payload),
      },
    );
  },
};
