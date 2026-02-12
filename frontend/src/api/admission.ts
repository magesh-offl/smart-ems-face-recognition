/**
 * Admin API Module
 * 
 * Provides API functions for admin-specific operations.
 * Uses the shared apiClient from client.ts which handles:
 * - Authentication token injection
 * - 401 error handling (auto-logout)
 * - Common error handling
 */
import apiClient from './client';

// Types
export interface Course {
    course_id: string;
    name: string;
    section: string;
    description: string;
    is_active: boolean;
}

export interface Student {
    student_id: string;
    admission_id: string;
    user_id: string;
    username: string;
    email: string;
    first_name: string;
    last_name: string;
    course_id: string;
    is_trained: boolean;
    training_status: string;
    date_of_birth: string;
    guardian_name: string;
    guardian_phone: string;
    address: string;
}

export interface StudentDetails {
    student_id: string;
    admission_id: string | null;
    user: {
        user_id: string | null;
        username: string | null;
        email: string | null;
        first_name: string;
        last_name: string;
    };
    student: {
        date_of_birth: string;
        guardian_name: string;
        guardian_phone: string;
        address: string;
        is_trained: boolean;
    };
    course: {
        course_id: string | null;
        name: string | null;
        section: string | null;
    };
    admission: {
        admission_id: string | null;
        academic_year: string | null;
        status: string | null;
    };
}

export interface PasswordResetRequest {
    id: string;
    user_id: string;
    username: string;
    role_name: string;
    new_password: string;
    course_id?: string;
    created_at: string;
    status: string;
}

// Course APIs
export async function getCourses(activeOnly = true): Promise<{ courses: Course[] }> {
    const response = await apiClient.get('/admission/courses', { params: { active_only: activeOnly } });
    return response.data;
}

export async function createCourse(data: { name: string; section: string; description?: string }) {
    const response = await apiClient.post('/admission/courses', data);
    return response.data;
}

// Student APIs
export async function getStudents(
    skip = 0, 
    limit = 50, 
    courseId?: string
): Promise<{ students: Student[]; total: number }> {
    const params: any = { skip, limit };
    if (courseId) params.course_id = courseId;
    
    const response = await apiClient.get('/admission/students', { params });
    return response.data;
}

export async function getStudent(studentId: string): Promise<StudentDetails> {
    const response = await apiClient.get(`/admission/students/${studentId}`);
    return response.data;
}

export async function checkGuardianPhone(phone: string, excludeStudentId?: string) {
    const params: any = { phone };
    if (excludeStudentId) params.exclude_student_id = excludeStudentId;
    
    const response = await apiClient.get('/admission/students/check-phone', { params });
    return response.data;
}

export interface AdmitStudentData {
    first_name: string;
    last_name: string;
    course_id: string;
    date_of_birth: string;
    guardian_name: string;
    guardian_phone: string;
    address?: string;
}

export async function admitStudent(data: AdmitStudentData) {
    const formData = new FormData();
    Object.entries(data).forEach(([key, value]) => {
        if (value !== undefined) formData.append(key, value);
    });
    
    const response = await apiClient.post('/admission/students/admit', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
}

export interface UpdateStudentData {
    first_name?: string;
    last_name?: string;
    date_of_birth?: string;
    guardian_name?: string;
    guardian_phone?: string;
    address?: string;
    course_id?: string;
}

export async function updateStudent(studentId: string, data: UpdateStudentData) {
    const formData = new FormData();
    Object.entries(data).forEach(([key, value]) => {
        if (value !== undefined && value !== null) formData.append(key, value);
    });
    
    const response = await apiClient.put(`/admission/students/${studentId}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
}

export async function uploadStudentImages(admissionId: string, images: File[]) {
    const formData = new FormData();
    images.forEach((img) => formData.append('images', img));
    
    const response = await apiClient.post(`/admission/students/${admissionId}/images`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
}

export async function trainStudentFace(admissionId: string) {
    const response = await apiClient.post(`/admission/students/${admissionId}/train`);
    return response.data;
}

// Password Reset APIs
export async function getPasswordResets(skip = 0, limit = 50): Promise<{ requests: PasswordResetRequest[]; pending_count: number }> {
    const response = await apiClient.get('/admission/password-resets', { params: { skip, limit } });
    return response.data;
}

export async function completePasswordReset(requestId: string) {
    const response = await apiClient.post(`/admission/password-resets/${requestId}/complete`);
    return response.data;
}
