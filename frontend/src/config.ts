// API Configuration
export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export const API_VERSION = 'v1';

// App Constants
export const APP_NAME = 'Smart EMS';
export const APP_DESCRIPTION = 'Education Management System with Face Recognition';

// Routes
export const ROUTES = {
    HOME: '/',
    LOGIN: '/login',
    DASHBOARD: '/dashboard',
    RECOGNITION: '/recognition',
    PERSONS: '/persons',
} as const;
