import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000, // 30 second timeout
});

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add response interceptor for better error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    if (error.response) {
      console.error('Response data:', error.response.data);
      console.error('Response status:', error.response.status);
      
      // Handle 401 Unauthorized - redirect to login
      if (error.response.status === 401) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
    } else if (error.request) {
      console.error('No response received:', error.request);
    } else {
      console.error('Error message:', error.message);
    }
    return Promise.reject(error);
  }
);

// Authentication API functions
export const login = (username: string, password: string) =>
  axios.post('http://localhost:8000/api/auth/login/', { username, password }).then((r) => r.data);

export const logout = (refreshToken: string) =>
  axios.post('http://localhost:8000/api/auth/logout/', { refresh: refreshToken });

export const getProfile = () =>
  api.get('/auth/profile/').then((r) => r.data);

export const updateProfile = (data: { openrouter_api_key?: string; preferred_model?: string }) =>
  api.put('/auth/profile/', data).then((r) => r.data);

export const register = (username: string, email: string, password: string) =>
  axios.post('http://localhost:8000/api/auth/register/', { username, email, password }).then((r) => r.data);

export const createJob = (data: { title: string; description: string; latex_cv: string }) =>
  api.post('/jobs/', data).then((r) => {
    console.log('Job created successfully:', r.data);
    return r.data;
  });

export const getJobs = () => api.get('/jobs/').then((r) => r.data);

export const getJob = (id: string) => api.get(`/jobs/${id}/`).then((r) => r.data);

export const runProcess = (jobId: string, maxRetries = 3) =>
  api.post(`/jobs/${jobId}/run_process/`, { max_retries: maxRetries }).then((r) => {
    console.log('Process started successfully:', r.data);
    return r.data;
  });

export const getProcessRuns = () => api.get('/process-runs/').then((r) => r.data);

export const getProcessRun = (id: string) => api.get(`/process-runs/${id}/`).then((r) => r.data);

export const getPrompt = (id: string) => 
  api.get(`/process-runs/${id}/get_prompt/`).then((r) => r.data);

export const submitManualLatex = (id: string, latexContent: string) =>
  api.post(`/process-runs/${id}/submit_manual_latex/`, { latex_content: latexContent }).then((r) => r.data);

export const continueIterating = (id: string) =>
  api.post(`/process-runs/${id}/continue_iterating/`).then((r) => r.data);

export const restartProcess = (id: string) =>
  api.post(`/process-runs/${id}/restart/`).then((r) => r.data);

export const forceComplete = (id: string) =>
  api.post(`/process-runs/${id}/force_complete/`).then((r) => r.data);
