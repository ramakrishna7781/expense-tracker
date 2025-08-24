// import axios from 'axios';

// const API_BASE_URL = 'http://localhost:8000'; // Your FastAPI backend URL

// const api = axios.create({
//   baseURL: API_BASE_URL,
// });

// // Interceptor to add the auth token to every request
// api.interceptors.request.use(
//   (config) => {
//     const token = localStorage.getItem('authToken');
//     if (token) {
//       config.headers['Authorization'] = `Bearer ${token}`;
//     }
//     return config;
//   },
//   (error) => {
//     return Promise.reject(error);
//   }
// );

// // Auth endpoints
// export const registerUser = (data) => api.post('/auth/register', data);
// export const loginUser = (data) => api.post('/auth/login', data);

// // Expense endpoints
// export const addExpense = (data) => api.post('/expense/add', data);
// export const listExpenses = (query) => api.get(`/expense/list?query=${query}`);
// export const suggestSpending = (query) => api.get(`/expense/suggest-spending?query=${query}`);
// export const setSalary = (salary) => api.post(`/expense/set-salary?salary_input=${salary}`);

// // PDF Download
// export const downloadPdf = async () => {
//   const response = await api.get('/expense/download/pdf', {
//     responseType: 'blob', // Important for file downloads
//   });
  
//   // Create a link and trigger the download
//   const url = window.URL.createObjectURL(new Blob([response.data]));
//   const link = document.createElement('a');
//   link.href = url;
//   const contentDisposition = response.headers['content-disposition'];
//   let filename = 'expense-report.pdf';
//   if (contentDisposition) {
//       const filenameMatch = contentDisposition.match(/filename="(.+)"/);
//       if (filenameMatch.length === 2)
//           filename = filenameMatch[1];
//   }
//   link.setAttribute('download', filename);
//   document.body.appendChild(link);
//   link.click();
//   link.remove();
// };


import axios from 'axios';

// const API_BASE_URL = 'http://localhost:8000'; // Your FastAPI backend URL
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

// Auth endpoints
export const registerUser = (data) => api.post('/auth/register', data);
export const loginUser = (data) => api.post('/auth/login', data);

// Expense endpoints
export const addExpense = (data) => api.post('/expense/add', data);
export const listExpenses = (query) => api.get(`/expense/list?query=${query}`);
export const suggestSpending = (query) => api.get(`/expense/suggest-spending?query=${query}`);
export const setSalary = (salary) => api.post(`/expense/set-salary?salary_input=${salary}`);
// ✅ ADD THIS NEW FUNCTION
export const getAnalytics = () => api.get('/expense/analytics');

// PDF Download
export const downloadPdf = async () => {
  const response = await api.get('/expense/download/pdf', {
    responseType: 'blob', // Important for file downloads
  });
  
  // Create a link and trigger the download
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  const contentDisposition = response.headers['content-disposition'];
  let filename = 'expense-report.pdf';
  if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="(.+)"/);
      if (filenameMatch.length === 2)
          filename = filenameMatch[1];
  }
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
};