import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Interceptor to add the auth token to every request
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// --- Auth endpoints (no change) ---
export const registerUser = (data) => api.post('/auth/register', data);
export const loginUser = (data) => api.post('/auth/login', data);


// --- NEW: The single endpoint for all chat messages ---
export const handleCommand = (data) => api.post('/command/', data);


// --- Direct-action endpoints for buttons (no change) ---
export const getAnalytics = () => api.get('/expense/analytics');

export const downloadPdf = async () => {
  const response = await api.get('/pdf/monthly', { // Using the dedicated pdf route
    responseType: 'blob',
  });
  
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  
  // Extract filename from headers, fallback to a default
  const contentDisposition = response.headers['content-disposition'];
  let filename = 'expense-report.pdf';
  if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="(.+)"/);
      if (filenameMatch && filenameMatch.length === 2) {
          filename = filenameMatch[1];
      }
  }
  
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
};