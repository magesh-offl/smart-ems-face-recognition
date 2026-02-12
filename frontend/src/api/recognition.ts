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

// Group Recognition Types
export interface RecognizedStudent {
    student_id: string;
    admission_id: string;
    first_name: string;
    last_name: string;
    course_name: string;
    section: string;
    confidence: number;
    face_location: {
        x_min: number;
        y_min: number;
        x_max: number;
        y_max: number;
    };
}

export interface GroupRecognitionResult {
    success: boolean;
    batch_id: string;
    stats: {
        total_faces_detected: number;
        recognized_count: number;
        unknown_count: number;
        processing_time_ms: number;
    };
    recognized: RecognizedStudent[];
    unknown_faces: Array<{ face_location: { note?: string } }>;
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
    const response = await apiClient.get('/admission/known-persons');
    return response.data;
};

// Add persons from folder
export const addPersons = async (sourcePath?: string) => {
    const response = await apiClient.post('/recognition/persons/add', { source_path: sourcePath });
    return response.data;
};

// Recognize students from group photo
export const recognizeGroup = async (imageFile: File): Promise<GroupRecognitionResult> => {
    const formData = new FormData();
    formData.append('image', imageFile);
    
    const response = await apiClient.post('/admission/recognize-group', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};

// History log type
export interface RecognitionHistoryLog {
    id: string;
    student_id: string;
    admission_id: string;
    first_name: string;
    last_name: string;
    course_name: string;
    section: string;
    confidence: number;
    detection_datetime: string;
    batch_id: string;
}

export interface RecognitionHistoryResult {
    success: boolean;
    total: number;
    skip: number;
    limit: number;
    logs: RecognitionHistoryLog[];
}

// Get recognition history with filters
export const getRecognitionHistory = async (params: {
    student_id?: string;
    course_id?: string;
    start_date?: string;
    end_date?: string;
    skip?: number;
    limit?: number;
}): Promise<RecognitionHistoryResult> => {
    const response = await apiClient.get('/admission/recognition-history', { params });
    return response.data;
};


