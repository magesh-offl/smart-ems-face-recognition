import axios from 'axios';
import { API_URL, API_VERSION } from '../config';

// Create Axios instance
export const apiClient = axios.create({
    baseURL: `${API_URL}/api/${API_VERSION}`,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor - Add auth token
apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        const apiKey = localStorage.getItem('apiKey');

        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        if (apiKey) {
            config.headers['X-API-Key'] = apiKey;
        }

        return config;
    },
    (error) => Promise.reject(error)
);

// Response interceptor - Handle errors globally
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // Clear all auth data on unauthorized
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            localStorage.removeItem('apiKey');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

export default apiClient;
