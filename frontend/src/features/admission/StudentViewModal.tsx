import { useEffect, useState } from 'react';
import { format, parseISO } from 'date-fns';
import { getStudent, type StudentDetails } from '../../api/admission';
import styles from './StudentModal.module.css';

interface StudentViewModalProps {
    studentId: string;
    onClose: () => void;
}

export default function StudentViewModal({ studentId, onClose }: StudentViewModalProps) {
    const [details, setDetails] = useState<StudentDetails | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        loadDetails();
    }, [studentId]);

    const loadDetails = async () => {
        try {
            setLoading(true);
            const data = await getStudent(studentId);
            setDetails(data);
        } catch (err: any) {
            setError(err?.response?.data?.detail || 'Failed to load student details');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={styles.overlay} onClick={onClose}>
            <div className={styles.modal} onClick={e => e.stopPropagation()}>
                <div className={styles.header}>
                    <h3>📋 Student Details</h3>
                    <button className={styles.closeBtn} onClick={onClose}>×</button>
                </div>

                {loading && <div className={styles.loadingOverlay}>Loading...</div>}
                {error && <div className={styles.error}>{error}</div>}

                {details && (
                    <div className={styles.detailGrid}>
                        <div className={styles.sectionTitle}>Identification</div>
                        <DetailRow label="Student ID" value={details.student_id} mono />
                        <DetailRow label="Admission ID" value={details.admission_id || '—'} mono />

                        <div className={styles.sectionTitle}>Personal</div>
                        <DetailRow label="First Name" value={details.user.first_name || '—'} />
                        <DetailRow label="Last Name" value={details.user.last_name || '—'} />
                        <DetailRow 
                            label="Date of Birth" 
                            value={details.student.date_of_birth ? format(parseISO(details.student.date_of_birth), 'dd-MM-yyyy') : '—'} 
                        />

                        <div className={styles.sectionTitle}>Course</div>
                        <DetailRow 
                            label="Course" 
                            value={details.course.name 
                                ? `${details.course.name}${details.course.section ? ` - ${details.course.section}` : ''}`
                                : '—'} 
                        />
                        <DetailRow label="Academic Year" value={details.admission.academic_year || '—'} />
                        <DetailRow label="Status" value={details.admission.status || '—'} />

                        <div className={styles.sectionTitle}>Guardian</div>
                        <DetailRow label="Guardian" value={details.student.guardian_name || '—'} />
                        <DetailRow label="Phone" value={details.student.guardian_phone || '—'} />
                        <DetailRow label="Address" value={details.student.address || '—'} />

                        <div className={styles.sectionTitle}>Face Training</div>
                        <div className={styles.detailRow}>
                            <span className={styles.detailLabel}>Trained</span>
                            <span className={`${styles.badge} ${details.student.is_trained ? styles.badgeTrained : styles.badgeUntrained}`}>
                                {details.student.is_trained ? '✓ Trained' : '○ Not Trained'}
                            </span>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

function DetailRow({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
    return (
        <div className={styles.detailRow}>
            <span className={styles.detailLabel}>{label}</span>
            <span className={`${styles.detailValue} ${mono ? styles.mono : ''}`}>{value}</span>
        </div>
    );
}
