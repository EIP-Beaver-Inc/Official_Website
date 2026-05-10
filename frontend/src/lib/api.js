import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
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
