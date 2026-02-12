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
    FORGOT_PASSWORD: '/forgot-password',
    DASHBOARD: '/dashboard',
    RECOGNITION: '/recognition',
    PERSONS: '/persons',
    ADMISSION: '/admission',
    ADMISSION_STUDENTS: '/admission/students',
    ADMISSION_COURSES: '/admission/courses',
    ADMISSION_PASSWORD_RESETS: '/admission/password-resets',
} as const;

