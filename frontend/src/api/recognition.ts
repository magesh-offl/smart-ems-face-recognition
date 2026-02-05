import apiClient from './client';

// Types
export interface RecognitionLog {
    _id: string;
    person_name: string;
    detection_datetime: string;
    confidence_score: number;
    camera_id?: string;
}

export interface BatchResult {
    _id: string;
    image_path: string;
    total_faces: number;
    recognized_count: number;
    unknown_count: number;
    results: RecognitionLog[];
}

export interface Person {
    name: string;
    image_count: number;
}

// Get recognition logs
export const getLogs = async (skip = 0, limit = 10) => {
    const response = await apiClient.get('/recognition/logs', { params: { skip, limit } });
    return response.data;
};

// Process batch image
export const processBatch = async (imagePath: string) => {
    const response = await apiClient.post('/recognition/batch/process', { image_path: imagePath });
    return response.data;
};

// Get all batches
export const getBatches = async (skip = 0, limit = 10) => {
    const response = await apiClient.get('/recognition/batches', { params: { skip, limit } });
    return response.data;
};

// Get known persons
export const getPersons = async () => {
    const response = await apiClient.get('/recognition/persons');
    return response.data;
};

// Add persons from folder
export const addPersons = async (sourcePath?: string) => {
    const response = await apiClient.post('/recognition/persons/add', { source_path: sourcePath });
    return response.data;
};
