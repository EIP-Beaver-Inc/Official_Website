import axios from 'axios';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL ?? 'http://localhost:8001';
export const API = `${BACKEND_URL}/api`;

export const api = axios.create({
    baseURL: API,
    headers: { 'Content-Type': 'application/json' },
    timeout: 20000,
});

export async function fetchPipeline() {
    const r = await api.get('/pipeline');
    return r.data;
}

export async function fetchDefects() {
    const r = await api.get('/defects');
    return r.data;
}

export async function fetchScoring() {
    const r = await api.get('/scoring');
    return r.data;
}

export async function fetchQuiz() {
    const r = await api.get('/quiz/questions');
    return r.data;
}

export async function submitQuiz(payload) {
    const r = await api.post('/quiz/submit', payload);
    return r.data;
}

export async function submitContact(payload) {
    const r = await api.post('/contact', payload);
    return r.data;
}

export async function submitDemoRequest(payload) {
    const r = await api.post('/demo-requests', payload);
    return r.data;
}

// ---- Beta ----
export async function validateBetaKey(payload) {
    const r = await api.post('/beta/validate', payload);
    return r.data;
}

function betaHeaders() {
    const token = localStorage.getItem('beaver_beta_token');
    return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function fetchBetaMe() {
    const r = await api.get('/beta/me', { headers: betaHeaders() });
    return r.data;
}

export async function fetchTutorials() {
    const r = await api.get('/beta/tutorials', { headers: betaHeaders() });
    return r.data.tutorials;
}

// ---- Admin ----
export async function adminLogin(password) {
    const r = await api.post('/admin/login', { password });
    return r.data;
}

function adminHeaders() {
    const token = localStorage.getItem('beaver_admin_token');
    return token ? { 'X-Admin-Token': token } : {};
}

export async function adminGenerateKey(payload) {
    const r = await api.post('/admin/beta/generate', payload, { headers: adminHeaders() });
    return r.data;
}

export async function adminListKeys() {
    const r = await api.get('/admin/beta/keys', { headers: adminHeaders() });
    return r.data;
}

export async function adminListClients() {
    const r = await api.get('/admin/beta/clients', { headers: adminHeaders() });
    return r.data;
}

export async function adminDeleteClient(clientId) {
    const r = await api.delete(`/admin/beta/clients/${clientId}`, { headers: adminHeaders() });
    return r.data;
}
