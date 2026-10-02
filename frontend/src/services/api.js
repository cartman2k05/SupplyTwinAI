const BASE_URL = '';

export async function apiFetch(endpoint, options = {}) {
  const token = localStorage.getItem('token');
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  };

  const config = {
    ...options,
    headers,
  };

  const response = await fetch(`${BASE_URL}${endpoint}`, config);

  if (response.status === 401) {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login';
    throw new Error('Unauthorized');
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `API error: ${response.status}`);
  }

  return response.json();
}

export const authApi = {
  login: async (username, password) => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const res = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Login failed');
    }
    return res.json();
  },
  getMe: () => apiFetch('/api/v1/auth/me'),
};

export const dataApi = {
  getOrders: (limit = 50) => apiFetch(`/api/v1/orders/?limit=${limit}`),
  getShipments: (limit = 50) => apiFetch(`/api/v1/shipments/?limit=${limit}`),
  getInventory: (limit = 50) => apiFetch(`/api/v1/inventory/?limit=${limit}`),
  getSuppliers: (limit = 50) => apiFetch(`/api/v1/suppliers/?limit=${limit}`),
  getAdminConfig: () => apiFetch('/api/v1/admin/config'),
  updateAdminConfig: (data) =>
    apiFetch('/api/v1/admin/config', {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
};
