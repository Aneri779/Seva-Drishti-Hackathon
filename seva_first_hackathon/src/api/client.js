// src/api/client.js
const BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1';

export async function api(path, { method = 'GET', body, form } = {}) {
  const token = sessionStorage.getItem('sd_token');
  const headers = {};
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  if (body) {
    headers['Content-Type'] = 'application/json';
  }

  const res = await fetch(BASE + path, {
    method,
    headers,
    body: form ?? (body ? JSON.stringify(body) : undefined),
  });

  if (res.status === 401) {
    sessionStorage.removeItem('sd_token');
    sessionStorage.removeItem('sd_user');
    if (!window.location.pathname.includes('/login')) {
      window.location.href = '/login';
    }
  }

  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || res.statusText || 'API Request Failed');
  }

  return res.json();
}

api.get = (path) => api(path, { method: 'GET' });
api.post = (path, body) => api(path, { method: 'POST', body });
api.patch = (path, body) => api(path, { method: 'PATCH', body });
api.delete = (path) => api(path, { method: 'DELETE' });

