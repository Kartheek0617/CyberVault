import axios from 'axios';

const api = axios.create({
    baseURL: '/api',
    headers: { 'Content-Type': 'application/json' },
});

// Attach JWT token to every request
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('cv_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Handle 401 globally — redirect to login
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('cv_token');
            localStorage.removeItem('cv_user');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// ── Auth ──────────────────────────────────────────────────────────────────
export const authApi = {
    login: (credentials) => api.post('/auth/login', credentials),
    logout: () => api.post('/auth/logout'),
    me: () => api.get('/auth/me'),
};

// ── Users ──────────────────────────────────────────────────────────────────
export const usersApi = {
    list: () => api.get('/users'),
    get: (id) => api.get(`/users/${id}`),
    create: (data) => api.post('/users', data),
    update: (id, data) => api.put(`/users/${id}`, data),
};

// ── Cases ──────────────────────────────────────────────────────────────────
export const casesApi = {
    list: (statusFilter) => api.get('/cases', { params: { status_filter: statusFilter } }),
    get: (id) => api.get(`/cases/${id}`),
    create: (data) => api.post('/cases', data),
    update: (id, data) => api.put(`/cases/${id}`, data),
    addMember: (caseId, data) => api.post(`/cases/${caseId}/members`, data),
    listEvidences: (caseId) => api.get(`/cases/${caseId}/evidence`),
    listReports: (caseId) => api.get(`/cases/${caseId}/reports`),
    createReport: (caseId, data) => api.post(`/cases/${caseId}/reports`, data),
};

// ── Evidence ──────────────────────────────────────────────────────────────
export const evidenceApi = {
    upload: (caseId, formData) => api.post(`/cases/${caseId}/evidence`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
    }),
    get: (id) => api.get(`/evidence/${id}`),
    verify: (id) => api.post(`/evidence/${id}/verify`),
    transfer: (id, data) => api.post(`/evidence/${id}/transfer`, data),
    receive: (id) => api.post(`/evidence/${id}/receive`),
    getCustody: (id) => api.get(`/evidence/${id}/custody`),
};

// ── Reports ────────────────────────────────────────────────────────────────
export const reportsApi = {
    get: (id) => api.get(`/reports/${id}`),
    verifySignature: (id) => api.post(`/reports/${id}/verify-signature`),
};

// ── Audit ──────────────────────────────────────────────────────────────────
export const auditApi = {
    list: (params) => api.get('/audit', { params }),
    verify: () => api.post('/audit/verify'),
};

// ── Dashboard ──────────────────────────────────────────────────────────────
export const dashboardApi = {
    stats: () => api.get('/dashboard/stats'),
    recentActivity: () => api.get('/dashboard/recent-activity'),
    securityEvents: () => api.get('/dashboard/security-events'),
};

export default api;
