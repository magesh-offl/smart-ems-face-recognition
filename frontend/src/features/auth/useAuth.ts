import { useState, useCallback, useMemo } from 'react';
import { login, register, forgotPassword } from '../../api/auth';
import type { LoginCredentials, TokenResponse } from '../../api/auth';

// User info returned from login
interface UserInfo {
    user_id: string;
    username: string;
    email: string;
    role_id: string;
    role: string | null;
    first_name: string;
    last_name: string;
}

interface AuthState {
    isAuthenticated: boolean;
    token: string | null;
    user: UserInfo | null;
    isLoading: boolean;
    error: string | null;
}

// Permission checking helper
const ROLE_PERMISSIONS: Record<string, string[]> = {
    super_admin: ['*'],
    admin: ['manage_teachers', 'manage_students', 'manage_roles', 'manage_courses', 'view_dashboard', 'view_reset_requests'],
    teacher: ['manage_students', 'view_dashboard'],
    student: ['view_own_profile'],
};

export function useAuth() {
    const [state, setState] = useState<AuthState>(() => {
        const token = localStorage.getItem('token');
        const userStr = localStorage.getItem('user');
        return {
            isAuthenticated: !!token,
            token,
            user: userStr ? JSON.parse(userStr) : null,
            isLoading: false,
            error: null,
        };
    });

    const handleLogin = useCallback(async (credentials: LoginCredentials) => {
        setState((prev) => ({ ...prev, isLoading: true, error: null }));
        try {
            const response: TokenResponse = await login(credentials);
            console.log('Login response:', response); // Debug logging
            
            localStorage.setItem('token', response.access_token);
            
            // Store user info from response
            const user = response.user;
            console.log('User from response:', user); // Debug logging
            if (user) {
                localStorage.setItem('user', JSON.stringify(user));
            } else {
                console.warn('No user object in login response');
            }
            
            setState({
                isAuthenticated: true,
                token: response.access_token,
                user: user || null,
                isLoading: false,
                error: null,
            });
            return true;
        } catch (error: unknown) {
            console.error('Login error:', error); // Debug logging
            const message = error instanceof Error ? error.message : 'Login failed';
            setState((prev) => ({ ...prev, isLoading: false, error: message }));
            return false;
        }
    }, []);

    const handleRegister = useCallback(async (
        username: string, 
        password: string, 
        email: string
    ) => {
        setState((prev) => ({ ...prev, isLoading: true, error: null }));
        try {
            await register({ username, password, email });
            setState((prev) => ({ ...prev, isLoading: false }));
            return true;
        } catch (error: unknown) {
            const message = error instanceof Error ? error.message : 'Registration failed';
            setState((prev) => ({ ...prev, isLoading: false, error: message }));
            return false;
        }
    }, []);

    const handleForgotPassword = useCallback(async (username: string) => {
        setState((prev) => ({ ...prev, isLoading: true, error: null }));
        try {
            const result = await forgotPassword(username);
            setState((prev) => ({ ...prev, isLoading: false }));
            return result;
        } catch (error: unknown) {
            const message = error instanceof Error ? error.message : 'Request failed';
            setState((prev) => ({ ...prev, isLoading: false, error: message }));
            throw error;
        }
    }, []);

    const handleLogout = useCallback(() => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        setState({
            isAuthenticated: false,
            token: null,
            user: null,
            isLoading: false,
            error: null,
        });
    }, []);

    // Permission checking
    const hasPermission = useCallback((permission: string): boolean => {
        if (!state.user?.role) return false;
        const permissions = ROLE_PERMISSIONS[state.user.role] || [];
        return permissions.includes('*') || permissions.includes(permission);
    }, [state.user]);

    const hasRole = useCallback((roles: string | string[]): boolean => {
        if (!state.user?.role) return false;
        const roleList = Array.isArray(roles) ? roles : [roles];
        return roleList.includes(state.user.role);
    }, [state.user]);

    // Check if user is admin or super_admin
    const isAdmin = useMemo(() => 
        hasRole(['super_admin', 'admin']), 
        [hasRole]
    );

    return {
        ...state,
        login: handleLogin,
        register: handleRegister,
        logout: handleLogout,
        forgotPassword: handleForgotPassword,
        hasPermission,
        hasRole,
        isAdmin,
    };
}
