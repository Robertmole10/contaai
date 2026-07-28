import { apiFetch } from '../lib/api';
import type { User } from '../types/workspace';

export const authService = {
  getCurrentUser(): Promise<User> {
    return apiFetch<User>('/auth/me');
  },

  refresh(): Promise<void> {
    return apiFetch<void>('/auth/refresh', {
      method: 'POST',
    });
  },

  logout(): Promise<void> {
    return apiFetch<void>('/auth/logout', {
      method: 'POST',
    });
  },
};
