import { useState, useCallback } from 'react';
import { login, register, LoginCredentials, TokenResponse } from '../../api/auth';

interface AuthState {
    isAuthenticated: boolean;
    token: string | null;
    isLoading: boolean;
    error: string | null;
}

export function useAuth() {
    const [state, setState] = useState<AuthState>(() => ({
        isAuthenticated: !!localStorage.getItem('token'),
        token: localStorage.getItem('token'),
        isLoading: false,
        error: null,
    }));

    const handleLogin = useCallback(async (credentials: LoginCredentials) => {
        setState((prev) => ({ ...prev, isLoading: true, error: null }));
        try {
            const response: TokenResponse = await login(credentials);
            localStorage.setItem('token', response.access_token);
            setState({
                isAuthenticated: true,
                token: response.access_token,
                isLoading: false,
                error: null,
            });
            return true;
        } catch (error: unknown) {
            const message = error instanceof Error ? error.message : 'Login failed';
            setState((prev) => ({ ...prev, isLoading: false, error: message }));
            return false;
        }
    }, []);

    const handleRegister = useCallback(async (username: string, password: string) => {
        setState((prev) => ({ ...prev, isLoading: true, error: null }));
        try {
            await register({ username, password });
            setState((prev) => ({ ...prev, isLoading: false }));
            return true;
        } catch (error: unknown) {
            const message = error instanceof Error ? error.message : 'Registration failed';
            setState((prev) => ({ ...prev, isLoading: false, error: message }));
            return false;
        }
    }, []);

    const handleLogout = useCallback(() => {
        localStorage.removeItem('token');
        setState({
            isAuthenticated: false,
            token: null,
            isLoading: false,
            error: null,
        });
    }, []);

    return {
        ...state,
        login: handleLogin,
        register: handleRegister,
        logout: handleLogout,
    };
}
