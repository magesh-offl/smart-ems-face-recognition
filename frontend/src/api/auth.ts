import apiClient from './client';

export interface LoginCredentials {
    username: string;
    password: string;
}

export interface UserInfo {
    user_id: string;
    username: string;
    email: string;
    role_id: string;
    role: string | null;
    first_name: string;
    last_name: string;
}

export interface TokenResponse {
    access_token: string;
    token_type: string;
    expires_in: number;
    user?: UserInfo;
}

export interface RegisterData {
    username: string;
    password: string;
    email: string;
    role_id?: string;
    first_name?: string;
    last_name?: string;
}

// Login
export const login = async (credentials: LoginCredentials): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>('/auth/login', credentials);
    return response.data;
};

// Register
export const register = async (data: RegisterData): Promise<{ success: boolean; message: string }> => {
    const response = await apiClient.post('/auth/register', data);
    return response.data;
};

// Forgot Password
export const forgotPassword = async (username: string): Promise<{ message: string }> => {
    const response = await apiClient.post<{ message: string }>('/auth/forgot-password', { username });
    return response.data;
};
