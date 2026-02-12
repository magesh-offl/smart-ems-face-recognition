import { useState, useEffect, useMemo } from 'react';
import { Upload, RefreshCw, Search } from 'lucide-react';
import { getStudents, getCourses, type Student, type Course } from '../../api/admission';
import { ImageUploadModal } from './ImageUploadModal';
import StudentViewModal from './StudentViewModal';
import StudentEditModal from './StudentEditModal';
import styles from './StudentList.module.css';

interface StudentListProps {
    onAdmitClick?: () => void;
}

export function StudentList({ onAdmitClick }: StudentListProps) {
    const [students, setStudents] = useState<Student[]>([]);
    const [courses, setCourses] = useState<Course[]>([]);
    const [selectedCourse, setSelectedCourse] = useState<string>('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [searchTerm, setSearchTerm] = useState('');
    const [statusFilter, setStatusFilter] = useState<string>('');
    const [uploadingStudent, setUploadingStudent] = useState<Student | null>(null);
    const [viewingStudentId, setViewingStudentId] = useState<string | null>(null);
    const [editingStudentId, setEditingStudentId] = useState<string | null>(null);

    useEffect(() => {
        loadCourses();
    }, []);

    useEffect(() => {
        loadStudents();
    }, [selectedCourse]);

    const loadCourses = async () => {
        try {
            const data = await getCourses();
            setCourses(data.courses);
        } catch (err) {
            console.error('Failed to load courses', err);
        }
    };

    const loadStudents = async () => {
        try {
            setLoading(true);
            const data = await getStudents(0, 50, selectedCourse || undefined);
            setStudents(data.students);
            setError('');
        } catch (err) {
            setError('Failed to load students');
        } finally {
            setLoading(false);
        }
    };


    // Client-side search + status filter
    const filteredStudents = useMemo(() => {
        return students.filter(s => {
            // Search filter
            if (searchTerm) {
                const term = searchTerm.toLowerCase();
                const matchesSearch =
                    s.student_id.toLowerCase().includes(term) ||
                    (s.admission_id || '').toLowerCase().includes(term) ||
                    `${s.first_name} ${s.last_name}`.toLowerCase().includes(term);
                if (!matchesSearch) return false;
            }
            // Status filter
            if (statusFilter === 'trained' && !s.is_trained) return false;
            if (statusFilter === 'pending' && s.is_trained) return false;
            return true;
        });
    }, [students, searchTerm, statusFilter]);

    const handleUpload = (student: Student) => {
        setUploadingStudent(student);
    };

    const handleUploadComplete = async (success: boolean) => {
        if (success) {
            await loadStudents();
        }
        setUploadingStudent(null);
    };

    const getStatusBadge = (student: Student) => {
        if (student.is_trained) {
            return <span className={styles.trained}>✓ Trained</span>;
        }
        if (student.training_status === 'processing') {
            return <span className={styles.processing}>Processing...</span>;
        }
        return <span className={styles.pending}>Pending</span>;
    };

    const getInitials = (firstName: string, lastName: string) => {
        return `${firstName?.[0] || ''}${lastName?.[0] || ''}`.toUpperCase();
    };

    return (
        <div className={styles.container}>
            <div className={styles.fixedHeader}>
                <div className={styles.header}>
                    <h2>Students</h2>
                    <div className={styles.actions}>
                        {onAdmitClick && (
                            <button onClick={onAdmitClick} className={styles.admitBtn}>
                                + Admit Student
                            </button>
                        )}
                    </div>
                </div>

                <div className={styles.filterBar}>
                    <div className={styles.searchBox}>
                        <Search size={16} className={styles.searchIcon} />
                        <input
                            type="text"
                            placeholder="Search by name, student ID, or admission ID..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className={styles.searchInput}
                        />
                    </div>
                    <select
                        value={selectedCourse}
                        onChange={(e) => setSelectedCourse(e.target.value)}
                        className={styles.filter}
                    >
                        <option value="">All Courses</option>
                        {courses.map((c) => (
                            <option key={c.course_id} value={c.course_id}>
                                {c.name} - {c.section}
                            </option>
                        ))}
                    </select>
                    <select
                        value={statusFilter}
                        onChange={(e) => setStatusFilter(e.target.value)}
                        className={styles.filter}
                    >
                        <option value="">All Status</option>
                        <option value="trained">Trained</option>
                        <option value="pending">Pending</option>
                    </select>
                    <button onClick={loadStudents} className={styles.refreshBtn} title="Refresh">
                        <RefreshCw size={16} /> Refresh
                    </button>
                    {(searchTerm || selectedCourse || statusFilter) && (
                        <button
                            onClick={() => { setSearchTerm(''); setSelectedCourse(''); setStatusFilter(''); }}
                            className={styles.resetBtn}
                            title="Reset filters"
                        >
                            ✕ Reset
                        </button>
                    )}
                </div>

                {!loading && !error && students.length > 0 && (
                    <div className={styles.stats}>
                        <div className={styles.stat}>
                            <span className={styles.statValue}>{filteredStudents.length}</span>
                            <span className={styles.statLabel}>Total</span>
                        </div>
                        <div className={styles.stat}>
                            <span className={styles.statValue}>{filteredStudents.filter(s => s.is_trained).length}</span>
                            <span className={styles.statLabel}>Trained</span>
                        </div>
                        <div className={styles.stat}>
                            <span className={styles.statValue}>{filteredStudents.filter(s => !s.is_trained).length}</span>
                            <span className={styles.statLabel}>Pending</span>
                        </div>
                    </div>
                )}
            </div>

            <div className={styles.scrollContent}>
                {error && <div className={styles.error}>{error}</div>}

                {loading ? (
                    <div className={styles.loading}>Loading students...</div>
                ) : students.length === 0 ? (
                    <div className={styles.empty}>
                        <span className={styles.emptyIcon}>👤</span>
                        <p>No students found</p>
                        {onAdmitClick && (
                            <button onClick={onAdmitClick} className={styles.admitBtn}>
                                Admit First Student
                            </button>
                        )}
                    </div>
                ) : (
                    <div className={styles.grid}>
                        {filteredStudents.map((student) => (
                            <div key={student.student_id} className={styles.card}>
                                <div className={styles.cardHeader}>
                                    <div className={styles.avatar}>
                                        {getInitials(student.first_name, student.last_name)}
                                    </div>
                                    <div className={styles.cardActions}>
                                        <button
                                            onClick={() => setViewingStudentId(student.student_id)}
                                            className={styles.iconBtn}
                                            title="View details"
                                        >
                                            👁
                                        </button>
                                        <button
                                            onClick={() => setEditingStudentId(student.student_id)}
                                            className={styles.iconBtn}
                                            title="Edit student"
                                        >
                                            ✏️
                                        </button>
                                        {getStatusBadge(student)}
                                    </div>
                                </div>
                                <div className={styles.cardBody}>
                                    <h3>{student.first_name} {student.last_name}</h3>
                                    <p className={styles.studentId}>{student.student_id}</p>
                                    {student.admission_id && (
                                        <p className={styles.admissionId}>{student.admission_id}</p>
                                    )}
                                    <p className={styles.email}>{student.email}</p>
                                </div>
                                <div className={styles.cardFooter}>
                                    {!student.is_trained && (
                                        <div className={styles.trainedInfo}>
                                            <button
                                                onClick={() => handleUpload(student)}
                                                className={styles.primaryActionBtn}
                                                title="Upload face images & train"
                                            >
                                                <Upload size={16} /> Upload Faces
                                            </button>
                                        </div>
                                    )}
                                    {student.is_trained && (
                                        <div className={styles.trainedInfo}>
                                            <button
                                                onClick={() => handleUpload(student)}
                                                className={styles.primaryActionBtn}
                                                title="Update face images & retrain"
                                            >
                                                <RefreshCw size={16} /> Update Faces
                                            </button>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Image upload modal */}
            {uploadingStudent && (
                <ImageUploadModal
                    admissionId={uploadingStudent.admission_id}
                    studentId={uploadingStudent.student_id}
                    studentName={`${uploadingStudent.first_name} ${uploadingStudent.last_name}`}
                    onComplete={handleUploadComplete}
                    onClose={() => setUploadingStudent(null)}
                />
            )}

            {/* View student modal */}
            {viewingStudentId && (
                <StudentViewModal
                    studentId={viewingStudentId}
                    onClose={() => setViewingStudentId(null)}
                />
            )}

            {/* Edit student modal */}
            {editingStudentId && (
                <StudentEditModal
                    studentId={editingStudentId}
                    onClose={() => setEditingStudentId(null)}
                    onSaved={() => {
                        setEditingStudentId(null);
                        loadStudents();
                    }}
                />
            )}
        </div>
    );
}
