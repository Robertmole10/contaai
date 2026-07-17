export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

export async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', ...(options.headers ?? {}) },
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: 'A apărut o eroare.' }));
    throw new Error(body.detail ?? 'A apărut o eroare.');
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}
