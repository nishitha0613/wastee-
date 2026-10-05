/**
 * Centralized API Client & Service Layer for EcoCycle
 * Connects React frontend with FastAPI backend.
 */

export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Token Storage Keys
const TOKEN_KEY = 'ecocycle_token';
const USER_KEY = 'ecocycle_user';
const ROLE_KEY = 'ecocycle_user_role';

export const authStorage = {
  getToken: () => {
    try {
      return localStorage.getItem(TOKEN_KEY);
    } catch {
      return null;
    }
  },
  setToken: (token) => {
    try {
      localStorage.setItem(TOKEN_KEY, token);
    } catch (e) {
      console.warn('Could not save token:', e);
    }
  },
  getUser: () => {
    try {
      const data = localStorage.getItem(USER_KEY);
      return data ? JSON.parse(data) : null;
    } catch {
      return null;
    }
  },
  setUser: (user) => {
    try {
      localStorage.setItem(USER_KEY, JSON.stringify(user));
      if (user?.role) {
        localStorage.setItem(ROLE_KEY, user.role);
      }
    } catch (e) {
      console.warn('Could not save user:', e);
    }
  },
  getRole: () => {
    try {
      return localStorage.getItem(ROLE_KEY);
    } catch {
      return null;
    }
  },
  clear: () => {
    try {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
      localStorage.removeItem(ROLE_KEY);
    } catch (e) {
      console.warn('Could not clear auth storage:', e);
    }
  },
};

/**
 * Generic API request handler with automatic auth header injection
 */
async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const headers = { ...options.headers };

  const token = authStorage.getToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  // If body is NOT FormData, set application/json
  if (options.body && !(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }

  const config = {
    ...options,
    headers,
  };

  try {
    const response = await fetch(url, config);

    // Handle 401 Unauthorized (expired or invalid token)
    if (response.status === 401 && !endpoint.includes('/login') && !endpoint.includes('/register')) {
      authStorage.clear();
      window.dispatchEvent(new CustomEvent('ecocycle_unauthorized'));
    }

    const contentType = response.headers.get('content-type');
    const isJson = contentType && contentType.includes('application/json');
    const data = isJson ? await response.json() : await response.text();

    if (!response.ok) {
      const errorMessage =
        (isJson && data?.detail) ||
        (isJson && data?.message) ||
        `Request failed with status ${response.status}`;
      const error = new Error(errorMessage);
      error.status = response.status;
      error.data = data;
      throw error;
    }

    return data;
  } catch (error) {
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      error.message = 'Unable to connect to the server. Please ensure the backend is running.';
    }
    throw error;
  }
}

/**
 * Resolve relative image paths (/uploads/...) to full backend URLs
 */
export function getImageUrl(imagePath) {
  if (!imagePath) return '';
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://') || imagePath.startsWith('data:')) {
    return imagePath;
  }
  if (imagePath.startsWith('/uploads')) {
    return `${API_BASE_URL}${imagePath}`;
  }
  return imagePath;
}

// ----------------------------------------------------------------------
// 1. Authentication APIs
// ----------------------------------------------------------------------
export const authApi = {
  register: async ({ name, email, password }) => {
    return await request('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({ name, email, password }),
    });
  },

  login: async ({ email, password }) => {
    const data = await request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    if (data?.access_token) {
      authStorage.setToken(data.access_token);
      if (data.user) {
        authStorage.setUser(data.user);
      }
    }
    return data;
  },

  getMe: async () => {
    return await request('/api/auth/me', {
      method: 'GET',
    });
  },
};

// ----------------------------------------------------------------------
// 2. Waste Identification & Reports APIs
// ----------------------------------------------------------------------
export const wasteApi = {
  identify: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return await request('/api/waste/identify', {
      method: 'POST',
      body: formData,
    });
  },

  getReports: async (params = {}) => {
    const query = new URLSearchParams();
    if (params.page) query.append('page', params.page);
    if (params.limit) query.append('limit', params.limit);
    const qs = query.toString() ? `?${query.toString()}` : '';
    return await request(`/api/waste/reports${qs}`, {
      method: 'GET',
    });
  },

  getReportById: async (id) => {
    return await request(`/api/waste/reports/${id}`, {
      method: 'GET',
    });
  },

  deleteReport: async (id) => {
    return await request(`/api/waste/reports/${id}`, {
      method: 'DELETE',
    });
  },
};

// ----------------------------------------------------------------------
// 3. User Collection Requests APIs
// ----------------------------------------------------------------------
export const collectionApi = {
  create: async ({ waste_report_id, waste_type, quantity, location, additional_notes }) => {
    return await request('/api/collection-requests', {
      method: 'POST',
      body: JSON.stringify({
        waste_report_id,
        waste_type,
        quantity,
        location,
        additional_notes,
      }),
    });
  },

  getAll: async (params = {}) => {
    const query = new URLSearchParams();
    if (params.page) query.append('page', params.page);
    if (params.limit) query.append('limit', params.limit);
    const qs = query.toString() ? `?${query.toString()}` : '';
    return await request(`/api/collection-requests${qs}`, {
      method: 'GET',
    });
  },

  getById: async (id) => {
    return await request(`/api/collection-requests/${id}`, {
      method: 'GET',
    });
  },

  cancel: async (id) => {
    return await request(`/api/collection-requests/${id}`, {
      method: 'DELETE',
    });
  },
};

// ----------------------------------------------------------------------
// 4. Administrator Collection Management APIs
// ----------------------------------------------------------------------
export const adminApi = {
  getCollectionRequests: async (options = null) => {
    let qs = '';
    if (typeof options === 'string') {
      qs = options && options !== 'All' ? `?status=${encodeURIComponent(options.toLowerCase())}` : '';
    } else if (options && typeof options === 'object') {
      const query = new URLSearchParams();
      if (options.status && options.status !== 'All') query.append('status', options.status.toLowerCase());
      if (options.waste_type) query.append('waste_type', options.waste_type);
      if (options.from_date) query.append('from_date', options.from_date);
      if (options.to_date) query.append('to_date', options.to_date);
      if (options.search) query.append('search', options.search);
      if (options.page) query.append('page', options.page);
      if (options.limit) query.append('limit', options.limit);
      qs = query.toString() ? `?${query.toString()}` : '';
    }
    return await request(`/api/admin/collection-requests${qs}`, {
      method: 'GET',
    });
  },

  getCollectionRequestById: async (id) => {
    return await request(`/api/admin/collection-requests/${id}`, {
      method: 'GET',
    });
  },

  getCollectionStats: async () => {
    return await request('/api/admin/collection-requests/stats', {
      method: 'GET',
    });
  },

  acceptRequest: async (id) => {
    return await request(`/api/admin/collection-requests/${id}/accept`, {
      method: 'PATCH',
    });
  },

  rejectRequest: async (id, reason = '') => {
    return await request(`/api/admin/collection-requests/${id}/reject`, {
      method: 'PATCH',
      body: JSON.stringify({ reason }),
    });
  },

  scheduleRequest: async (id, scheduledDate) => {
    return await request(`/api/admin/collection-requests/${id}/schedule`, {
      method: 'PATCH',
      body: JSON.stringify({ scheduled_date: scheduledDate }),
    });
  },

  collectRequest: async (id) => {
    return await request(`/api/admin/collection-requests/${id}/collect`, {
      method: 'PATCH',
    });
  },

  completeRequest: async (id) => {
    return await request(`/api/admin/collection-requests/${id}/complete`, {
      method: 'PATCH',
    });
  },
};
