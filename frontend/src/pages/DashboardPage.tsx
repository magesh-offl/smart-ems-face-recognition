import { useQuery } from '@tanstack/react-query';
import { Users, UserCheck, ScanFace, GraduationCap, BookOpen, Clock } from 'lucide-react';
import { getPersons } from '../api/recognition';
import { getStudents, getCourses } from '../api/admission';
import { getRecognitionHistory, type RecognitionHistoryLog } from '../api/recognition';
import styles from './DashboardPage.module.css';

const formatDisplayDate = (dateStr: string) => {
    if (!dateStr) return '-';
    const normalizedDateStr = dateStr.endsWith('Z') ? dateStr : `${dateStr}Z`;
    const date = new Date(normalizedDateStr);
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    let hours = date.getHours();
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12;
    hours = hours ? hours : 12;
    return `${day}-${month}-${year}, ${hours}:${minutes} ${ampm}`;
};

export function DashboardPage() {
    // Fetch known persons count
    const { data: personsData } = useQuery({
        queryKey: ['dashboardPersons'],
        queryFn: getPersons,
    });

    // Fetch all students (with a large limit)
    const { data: studentsData } = useQuery({
        queryKey: ['dashboardStudents'],
        queryFn: () => getStudents(0, 1000),
    });

    // Fetch courses
    const { data: coursesData } = useQuery({
        queryKey: ['dashboardCourses'],
        queryFn: () => getCourses(),
    });

    // Fetch recent recognition logs
    const { data: recentLogs } = useQuery({
        queryKey: ['dashboardRecent'],
        queryFn: () => getRecognitionHistory({ skip: 0, limit: 10 }),
    });

    // Fetch today's recognition count
    const today = new Date();
    const startDate = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
    const { data: todayData } = useQuery({
        queryKey: ['dashboardToday', startDate],
        queryFn: () => getRecognitionHistory({ start_date: startDate, skip: 0, limit: 1 }),
    });
    const todayCount = todayData?.total || 0;

    const knownPersons = personsData?.count || 0;
    const totalStudents = studentsData?.students?.length || 0;
    const trainedStudents = studentsData?.students?.filter((s: any) => s.is_trained).length || 0;
    const pendingStudents = totalStudents - trainedStudents;
    const totalCourses = coursesData?.courses?.length || 0;
    const recentActivity: RecognitionHistoryLog[] = recentLogs?.logs || [];

    return (
        <div className={styles.container}>
            {/* Stats Grid */}
            <div className={styles.statsGrid}>
                <div className={`${styles.statCard} ${styles.cardPersons}`}>
                    <div className={styles.statIconWrap}>
                        <Users size={24} />
                    </div>
                    <div className={styles.statInfo}>
                        <span className={styles.statValue}>{knownPersons}</span>
                        <span className={styles.statLabel}>Known Persons</span>
                    </div>
                </div>

                <div className={`${styles.statCard} ${styles.cardRecognitions}`}>
                    <div className={styles.statIconWrap}>
                        <ScanFace size={24} />
                    </div>
                    <div className={styles.statInfo}>
                        <span className={styles.statValue}>{todayCount}</span>
                        <span className={styles.statLabel}>Recognitions Today</span>
                    </div>
                </div>

                <div className={`${styles.statCard} ${styles.cardTrained}`}>
                    <div className={styles.statIconWrap}>
                        <UserCheck size={24} />
                    </div>
                    <div className={styles.statInfo}>
                        <span className={styles.statValue}>{trainedStudents}<span className={styles.statSub}>/{totalStudents}</span></span>
                        <span className={styles.statLabel}>Trained Students</span>
                    </div>
                </div>

                <div className={`${styles.statCard} ${styles.cardCourses}`}>
                    <div className={styles.statIconWrap}>
                        <BookOpen size={24} />
                    </div>
                    <div className={styles.statInfo}>
                        <span className={styles.statValue}>{totalCourses}</span>
                        <span className={styles.statLabel}>Active Courses</span>
                    </div>
                </div>
            </div>

            {/* Summary Cards */}
            <div className={styles.summaryGrid}>
                <div className={styles.summaryCard}>
                    <div className={styles.summaryHeader}>
                        <GraduationCap size={20} />
                        <h3>Student Overview</h3>
                    </div>
                    <div className={styles.summaryBody}>
                        <div className={styles.summaryRow}>
                            <span>Total Students</span>
                            <span className={styles.summaryValue}>{totalStudents}</span>
                        </div>
                        <div className={styles.summaryRow}>
                            <span>Trained</span>
                            <span className={`${styles.summaryValue} ${styles.textGreen}`}>{trainedStudents}</span>
                        </div>
                        <div className={styles.summaryRow}>
                            <span>Pending Training</span>
                            <span className={`${styles.summaryValue} ${styles.textYellow}`}>{pendingStudents}</span>
                        </div>
                        {totalStudents > 0 && (
                            <div className={styles.progressBar}>
                                <div
                                    className={styles.progressFill}
                                    style={{ width: `${(trainedStudents / totalStudents) * 100}%` }}
                                />
                            </div>
                        )}
                        <span className={styles.progressLabel}>
                            {totalStudents > 0 ? Math.round((trainedStudents / totalStudents) * 100) : 0}% trained
                        </span>
                    </div>
                </div>

                <div className={styles.summaryCard}>
                    <div className={styles.summaryHeader}>
                        <BookOpen size={20} />
                        <h3>Courses</h3>
                    </div>
                    <div className={styles.summaryBody}>
                        {coursesData?.courses?.length ? (
                            coursesData.courses.map((course: any) => {
                                const courseStudents = studentsData?.students?.filter((s: any) => s.course_id === course.course_id).length || 0;
                                return (
                                    <div key={course.course_id} className={styles.summaryRow}>
                                        <span>{course.name} {course.section && `- ${course.section}`}</span>
                                        <span className={styles.summaryValue}>{courseStudents} students</span>
                                    </div>
                                );
                            })
                        ) : (
                            <p className={styles.emptyState}>No courses available</p>
                        )}
                    </div>
                </div>
            </div>

            {/* Recent Activity */}
            <div className={styles.section}>
                <div className={styles.sectionHeader}>
                    <Clock size={20} />
                    <h2 className={styles.sectionTitle}>Recent Recognitions</h2>
                </div>
                {recentActivity.length > 0 ? (
                    <div className={styles.activityList}>
                        {recentActivity.map((log, i) => (
                            <div key={log.id || i} className={styles.activityItem}>
                                <div className={styles.activityAvatar}>
                                    <ScanFace size={18} />
                                </div>
                                <div className={styles.activityContent}>
                                    <div className={styles.activityName}>
                                        {log.first_name} {log.last_name}
                                    </div>
                                    <div className={styles.activityMeta}>
                                        {log.course_name}{log.section && ` - ${log.section}`}
                                    </div>
                                </div>
                                <div className={styles.activityRight}>
                                    <span className={styles.activityConfidence}>
                                        {(log.confidence * 100).toFixed(0)}%
                                    </span>
                                    <span className={styles.activityTime}>
                                        {formatDisplayDate(log.detection_datetime)}
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <p className={styles.emptyState}>No recognition logs yet. Perform a group recognition to see activity here.</p>
                )}
            </div>
        </div>
    );
}
