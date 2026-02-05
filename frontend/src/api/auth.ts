import apiClient from './client';

export interface LoginCredentials {
    username: string;
    password: string;
}

export interface TokenResponse {
    access_token: string;
    token_type: string;
}

export interface RegisterData {
    username: string;
    password: string;
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
