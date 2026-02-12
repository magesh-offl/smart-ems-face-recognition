import { useEffect, useState } from 'react';
import { getStudent, updateStudent, getCourses, checkGuardianPhone, type StudentDetails, type Course, type UpdateStudentData } from '../../api/admission';
import { maskDateInput } from '../../utils/dateHelpers';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import { format, parseISO } from 'date-fns';
import styles from './StudentModal.module.css';

interface StudentEditModalProps {
    studentId: string;
    onClose: () => void;
    onSaved: () => void;
}

export default function StudentEditModal({ studentId, onClose, onSaved }: StudentEditModalProps) {
    const [details, setDetails] = useState<StudentDetails | null>(null);
    const [courses, setCourses] = useState<Course[]>([]);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState('');
    const [phoneError, setPhoneError] = useState('');
    const [success, setSuccess] = useState('');

    // Form fields
    const [firstName, setFirstName] = useState('');
    const [lastName, setLastName] = useState('');
    const [dateOfBirth, setDateOfBirth] = useState('');
    const [guardianName, setGuardianName] = useState('');
    const [guardianPhone, setGuardianPhone] = useState('');
    const [address, setAddress] = useState('');
    const [courseId, setCourseId] = useState('');
    const [originalCourseId, setOriginalCourseId] = useState('');

    const [dobInputValue, setDobInputValue] = useState('');

    useEffect(() => {
        if (studentId) {
            loadData();
        }
    }, [studentId]);

    useEffect(() => {
        if (details?.student?.date_of_birth) {
            setDobInputValue(format(parseISO(details.student.date_of_birth), 'dd-MM-yyyy'));
        }
    }, [details]);

    // ... (rest of loadData)

    const loadData = async () => {

        try {
            setLoading(true);
            const [studentData, courseData] = await Promise.all([
                getStudent(studentId),
                getCourses()
            ]);

            setDetails(studentData);
            setCourses(courseData.courses);

            // Populate form
            setFirstName(studentData.user.first_name || '');
            setLastName(studentData.user.last_name || '');
            setDateOfBirth(studentData.student.date_of_birth || '');
            setGuardianName(studentData.student.guardian_name || '');
            setGuardianPhone(studentData.student.guardian_phone || '');
            setAddress(studentData.student.address || '');
            setCourseId(studentData.course.course_id || '');
            setOriginalCourseId(studentData.course.course_id || '');
        } catch (err: any) {
            setError(err?.response?.data?.detail || 'Failed to load student details');
        } finally {
            setLoading(false);
        }
    };

    const courseChanged = courseId !== originalCourseId;

    const handleNameChange = (val: string, setter: (v: string) => void) => {
        if (/[^a-zA-Z\s]/.test(val)) return;
        setter(val);
    };

    const handlePhoneChange = (val: string) => {
        if (!/^\d*$/.test(val)) return;
        if (val.length > 10) return;

        setGuardianPhone(val);

        if (val.length === 10) {
            checkGuardianPhone(val, studentId) // Pass studentId to exclude self
                .then(res => {
                    if (res.exists) {
                        setPhoneError('Phone number already exists');
                    } else {
                        setPhoneError('');
                    }
                })
                .catch(() => {
                    // Ignore errors
                });
        } else {
            setPhoneError('');
        }
    };

    const handleSave = async () => {
        try {
            setSaving(true);
            setError('');
            setSuccess('');

            const data: UpdateStudentData = {};

            // Only send changed fields
            if (details) {
                if (firstName !== (details.user.first_name || '')) data.first_name = firstName;
                if (lastName !== (details.user.last_name || '')) data.last_name = lastName;
                if (dateOfBirth !== (details.student.date_of_birth || '')) data.date_of_birth = dateOfBirth;
                if (guardianName !== (details.student.guardian_name || '')) data.guardian_name = guardianName;
                if (guardianPhone !== (details.student.guardian_phone || '')) data.guardian_phone = guardianPhone;
                if (address !== (details.student.address || '')) data.address = address;
                if (courseChanged) data.course_id = courseId;
            }

            if (Object.keys(data).length === 0) {
                setError('No changes to save');
                return;
            }

            if (phoneError) {
                setError('Please correct the errors before saving.');
                setSaving(false);
                return;
            }
            
            // Check validations again just in case (e.g. user pasted value)
            if (data.guardian_phone && data.guardian_phone.length !== 10) {
                setError('Guardian Phone must be exactly 10 digits');
                setSaving(false);
                return;
            }

            const result = await updateStudent(studentId, data);

            if (result.course_changed) {
                setSuccess(`Updated! New Student ID: ${result.student_id}`);
            } else {
                setSuccess('Student updated successfully');
            }

            // Notify parent after short delay so user sees success
            setTimeout(() => {
                onSaved();
            }, 1200);
        } catch (err: any) {
            setError(err?.response?.data?.detail || 'Failed to update student');
        } finally {
            setSaving(false);
        }
    };

    return (
        <div className={styles.overlay} onClick={onClose}>
            <div className={styles.modal} onClick={e => e.stopPropagation()}>
                <div className={styles.header}>
                    <h3>✏️ Edit Student</h3>
                    <button className={styles.closeBtn} onClick={onClose}>×</button>
                </div>

                {loading && <div className={styles.loadingOverlay}>Loading...</div>}
                {error && <div className={styles.error}>{error}</div>}
                {success && <div className={styles.success}>{success}</div>}

                {details && !loading && (
                    <div className={styles.form}>
                        {/* Student ID — read-only */}
                        <div className={`${styles.formGroup} ${styles.disabledField}`}>
                            <label>Student ID</label>
                            <input value={details.student_id} disabled />
                        </div>

                        {/* Admission ID — read-only */}
                        <div className={`${styles.formGroup} ${styles.disabledField}`}>
                            <label>Admission ID</label>
                            <input value={details.admission_id || '—'} disabled />
                        </div>

                        <div className={styles.formGroup}>
                            <label>First Name</label>
                            <input
                                value={firstName}
                                onChange={e => handleNameChange(e.target.value, setFirstName)}
                                disabled={saving}
                            />
                        </div>

                        <div className={styles.formGroup}>
                            <label>Last Name</label>
                            <input
                                value={lastName}
                                onChange={e => handleNameChange(e.target.value, setLastName)}
                                disabled={saving}
                            />
                        </div>

                        <div className={styles.formGroup}>
                            <label>Date of Birth</label>
                            <DatePicker
                                selected={dateOfBirth ? parseISO(dateOfBirth) : null}
                                onChange={(date: Date | null) => {
                                    if (date) {
                                        setDateOfBirth(format(date, 'yyyy-MM-dd'));
                                        setDobInputValue(format(date, 'dd-MM-yyyy'));
                                    } else {
                                        setDateOfBirth('');
                                        setDobInputValue('');
                                    }
                                }}
                                onChangeRaw={(e) => {
                                    if (!e || !e.target) return;
                                    const val = (e.target as HTMLInputElement).value;
                                    if (e.type === 'change') {
                                        e.preventDefault();
                                        const masked = maskDateInput(val);
                                        setDobInputValue(masked);
                                        if (masked.length === 10) {
                                            const [d, m, y] = masked.split('-').map(Number);
                                            const date = new Date(y, m - 1, d);
                                            if (!isNaN(date.getTime()) && date.getFullYear() === y) {
                                                setDateOfBirth(format(date, 'yyyy-MM-dd'));
                                            }
                                        }
                                    }
                                }}
                                value={dobInputValue}
                                dateFormat="dd-MM-yyyy"
                                placeholderText="DD-MM-YYYY"
                                className={styles.datePicker}
                                isClearable
                                showMonthDropdown
                                showYearDropdown
                                dropdownMode="select"
                                maxDate={new Date()}
                                yearDropdownItemNumber={100}
                                scrollableYearDropdown
                                disabled={saving}
                                autoComplete="off"
                                shouldCloseOnSelect={true}
                                portalId="root"
                            />
                        </div>

                        <div className={styles.formGroup}>
                            <label>Course</label>
                            <select
                                value={courseId}
                                onChange={e => setCourseId(e.target.value)}
                                disabled={saving}
                            >
                                {courses.map(c => (
                                    <option key={c.course_id} value={c.course_id}>
                                        {c.name}{c.section ? ` - ${c.section}` : ''}
                                    </option>
                                ))}
                            </select>
                        </div>

                        {courseChanged && (
                            <div className={styles.courseWarning}>
                                ⚠️ Changing course will regenerate the Student ID
                            </div>
                        )}

                        <div className={styles.formGroup}>
                            <label>Guardian Name</label>
                            <input
                                value={guardianName}
                                onChange={e => handleNameChange(e.target.value, setGuardianName)}
                                disabled={saving}
                            />
                        </div>

                        <div className={styles.formGroup}>
                            <label>Guardian Phone</label>
                            <input
                                value={guardianPhone}
                                onChange={e => handlePhoneChange(e.target.value)}
                                disabled={saving}
                                className={phoneError ? styles.inputError : ''}
                            />
                            {phoneError && <span className={styles.errorMessage}>{phoneError}</span>}
                        </div>

                        <div className={styles.formGroup}>
                            <label>Address</label>
                            <textarea
                                value={address}
                                onChange={e => setAddress(e.target.value)}
                                disabled={saving}
                                placeholder="Optional"
                            />
                        </div>

                        <div className={styles.actions}>
                            <button
                                className={styles.cancelBtn}
                                onClick={onClose}
                                disabled={saving}
                            >
                                Cancel
                            </button>
                            <button
                                className={styles.saveBtn}
                                onClick={handleSave}
                                disabled={saving || !!success}
                            >
                                {saving ? 'Saving...' : 'Save Changes'}
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
