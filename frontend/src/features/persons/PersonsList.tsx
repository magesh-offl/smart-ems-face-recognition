import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getPersons } from '../../api/recognition';
import { getStudents, getCourses, type Student, type Course } from '../../api/admission';
import { RefreshCw } from 'lucide-react';
import styles from './PersonsList.module.css';

interface PersonWithDetails {
    admission_id: string;
    student_id: string;
    first_name: string;
    last_name: string;
    course_id: string;
    course_name: string;
    section: string;
    status: string;
}

export function PersonsList() {
    const [searchTerm, setSearchTerm] = useState('');
    const [courseFilter, setCourseFilter] = useState('');
    const [courses, setCourses] = useState<Course[]>([]);

    // Fetch known persons from face recognition database
    const { data: personsData, isLoading: personsLoading, isError: personsError, refetch } = useQuery({
        queryKey: ['knownPersons'],
        queryFn: getPersons
    });

    // Fetch all students to get details
    const { data: studentsData } = useQuery({
        queryKey: ['allStudents'],
        queryFn: () => getStudents(0, 1000)
    });

    // Load courses for filter
    useEffect(() => {
        getCourses().then(data => setCourses(data.courses || [])).catch(console.error);
    }, []);

    // Create a map of admission_id -> student details (npz keys are now admission_id)
    const admissionMap = new Map<string, Student>();
    if (studentsData?.students) {
        studentsData.students.forEach((student: Student) => {
            if (student.admission_id) {
                admissionMap.set(student.admission_id, student);
            }
        });
    }

    // Merge persons (admission_ids from npz) with student details
    const personsWithDetails: PersonWithDetails[] = (personsData?.persons || []).map((personId: string) => {
        const student = admissionMap.get(personId);
        const course = courses.find(c => c.course_id === student?.course_id);
        return {
            admission_id: personId,
            student_id: student?.student_id || personId,
            first_name: student?.first_name || 'Unknown',
            last_name: student?.last_name || '',
            course_id: student?.course_id || '',
            course_name: course?.name || 'Unknown',
            section: course?.section || '',
            status: student?.is_trained ? 'trained' : 'pending'
        };
    });

    // Filter persons
    const filteredPersons = personsWithDetails.filter(person => {
        const matchesSearch = !searchTerm || 
            person.student_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
            person.admission_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
            `${person.first_name} ${person.last_name}`.toLowerCase().includes(searchTerm.toLowerCase());
        
        const matchesCourse = !courseFilter || person.course_id === courseFilter;
        
        return matchesSearch && matchesCourse;
    });

    return (
        <div className={styles.container}>
            <div className={styles.fixedHeader}>
                <div className={styles.header}>
                    <div>
                        <h2 className={styles.title}>👥 Known Persons</h2>
                        <p className={styles.subtitle}>
                            Faces registered in the face recognition database
                        </p>
                    </div>
                    <div className={styles.stats}>
                        <div className={styles.statCard}>
                            <span className={styles.statValue}>{personsData?.count || 0}</span>
                            <span className={styles.statLabel}>Total Persons</span>
                        </div>
                    </div>
                </div>

                {/* Filters */}
                <div className={styles.filterBar}>
                    <div className={styles.searchBox}>
                        <span className={styles.searchIcon}>🔍</span>
                        <input
                            type="text"
                            placeholder="Search by name, student ID, or admission ID..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className={styles.searchInput}
                        />
                    </div>
                    <select
                        value={courseFilter}
                        onChange={(e) => setCourseFilter(e.target.value)}
                        className={styles.courseSelect}
                    >
                        <option value="">All Courses</option>
                        {courses.map(course => (
                            <option key={course.course_id} value={course.course_id}>
                                {course.name} {course.section && `- ${course.section}`}
                            </option>
                        ))}
                    </select>
                    <button onClick={() => refetch()} className={styles.refreshBtn}>
                        <RefreshCw size={16} /> Refresh
                    </button>
                    {(searchTerm || courseFilter) && (
                        <button
                            onClick={() => { setSearchTerm(''); setCourseFilter(''); }}
                            className={styles.resetBtn}
                            title="Reset filters"
                        >
                            ✕ Reset
                        </button>
                    )}
                </div>
            </div>

            <div className={styles.scrollContent}>
                {/* Loading State */}
                {personsLoading && (
                    <div className={styles.loading}>
                        <span className={styles.spinner}></span>
                        Loading known persons...
                    </div>
                )}

                {/* Error State */}
                {personsError && (
                    <div className={styles.error}>
                        ⚠️ Failed to load persons. Please try again.
                    </div>
                )}

                {/* Empty State */}
                {!personsLoading && !personsError && filteredPersons.length === 0 && (
                    <div className={styles.empty}>
                        <div className={styles.emptyIcon}>📭</div>
                        <h3>No Persons Found</h3>
                        <p>No face embeddings are registered in the database.</p>
                    </div>
                )}

                {/* Persons Grid */}
                {!personsLoading && filteredPersons.length > 0 && (
                    <>
                        <div className={styles.resultCount}>
                            Showing {filteredPersons.length} of {personsData?.count || 0} persons
                        </div>
                        <div className={styles.grid}>
                            {filteredPersons.map((person) => (
                                <div key={person.student_id} className={styles.card}>
                                    <div className={styles.cardAvatar}>
                                        <span className={styles.avatarIcon}>👤</span>
                                    </div>
                                    <div className={styles.cardContent}>
                                        <div className={styles.cardName}>
                                            {person.first_name} {person.last_name}
                                        </div>
                                        <div className={styles.cardId}>{person.student_id}</div>
                                        <div className={styles.cardAdmissionId}>{person.admission_id}</div>
                                        <div className={styles.cardCourse}>
                                            {person.course_name}
                                            {person.section && ` - ${person.section}`}
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}
