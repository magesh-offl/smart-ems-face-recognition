import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import DatePicker from 'react-datepicker';
import { format } from 'date-fns';
import 'react-datepicker/dist/react-datepicker.css';
import { getRecognitionHistory } from '../../api/recognition';
import { getCourses, type Course } from '../../api/admission';
import type { RecognitionHistoryLog } from '../../api/recognition';
import styles from './RecognitionHistory.module.css';

export function RecognitionHistory() {
    const [courses, setCourses] = useState<Course[]>([]);
    const [filters, setFilters] = useState({
        student_id: '',
        course_id: ''
    });
    const [startDate, setStartDate] = useState<Date | null>(null);
    const [endDate, setEndDate] = useState<Date | null>(null);
    const [appliedFilters, setAppliedFilters] = useState({
        student_id: '',
        course_id: '',
        start_date: '',
        end_date: ''
    });
    const [page, setPage] = useState(0);
    const limit = 20;

    // Load courses for dropdown
    useEffect(() => {
        const loadCourses = async () => {
            try {
                const data = await getCourses();
                setCourses(data.courses || []);
            } catch (error) {
                console.error('Failed to load courses:', error);
            }
        };
        loadCourses();
    }, []);

    const { data, isLoading, isError } = useQuery({
        queryKey: ['recognitionHistory', appliedFilters, page],
        queryFn: () => getRecognitionHistory({
            ...appliedFilters,
            skip: page * limit,
            limit
        })
    });

    const handleSearch = () => {
        setPage(0);
        setAppliedFilters({
            ...filters,
            start_date: startDate ? format(startDate, 'yyyy-MM-dd') : '',
            end_date: endDate ? format(endDate, 'yyyy-MM-dd') : ''
        });
    };

    const handleReset = () => {
        setFilters({ student_id: '', course_id: '' });
        setStartDate(null);
        setEndDate(null);
        setAppliedFilters({ student_id: '', course_id: '', start_date: '', end_date: '' });
        setPage(0);
    };

    const formatDisplayDate = (dateStr: string) => {
        if (!dateStr) return '-';
        // Ensure date is treated as UTC if it comes as naive ISO string
        const normalizedDateStr = dateStr.endsWith('Z') ? dateStr : `${dateStr}Z`;
        const date = new Date(normalizedDateStr);
        
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const year = date.getFullYear();
        let hours = date.getHours();
        const minutes = String(date.getMinutes()).padStart(2, '0');
        const ampm = hours >= 12 ? 'PM' : 'AM';
        hours = hours % 12;
        hours = hours ? hours : 12; // 0 becomes 12
        return `${day}-${month}-${year}, ${hours}:${minutes} ${ampm}`;
    };

    const getConfidenceClass = (confidence: number): string => {
        if (confidence >= 0.8) return styles.highConfidence;
        if (confidence >= 0.6) return styles.mediumConfidence;
        return styles.lowConfidence;
    };

    const totalPages = data ? Math.ceil(data.total / limit) : 0;

    return (
        <div className={styles.container}>
            <div className={styles.fixedHeader}>
                <h2 className={styles.title}>📋 Recognition History</h2>
                <p className={styles.subtitle}>
                    Search and filter past face recognition records
                </p>

                {/* Filters */}
                <div className={styles.filterBar}>
                    <div className={styles.filterGroup}>
                        <label>Student ID</label>
                        <input
                            type="text"
                            placeholder="e.g., STU260050001"
                            value={filters.student_id}
                            onChange={(e) => setFilters({ ...filters, student_id: e.target.value })}
                        />
                    </div>
                    <div className={styles.filterGroup}>
                        <label>Course</label>
                        <select
                            value={filters.course_id}
                            onChange={(e) => setFilters({ ...filters, course_id: e.target.value })}
                            className={styles.select}
                        >
                            <option value="">All Courses</option>
                            {courses.map((course) => {
                                const displayName = course.section 
                                    ? `${course.name} - ${course.section}` 
                                    : course.name;
                                return (
                                    <option key={course.course_id} value={course.course_id}>
                                        {displayName}
                                    </option>
                                );
                            })}
                        </select>
                    </div>
                    <div className={styles.filterGroup}>
                        <label>From Date</label>
                        <DatePicker
                            selected={startDate}
                            onChange={(date: Date | null) => setStartDate(date)}
                            dateFormat="dd-MM-yyyy"
                            placeholderText="DD-MM-YYYY"
                            className={styles.datePicker}
                            isClearable
                            showMonthDropdown
                            showYearDropdown
                            dropdownMode="select"
                            maxDate={endDate || undefined}
                            portalId="root"
                        />
                    </div>
                    <div className={styles.filterGroup}>
                        <label>To Date</label>
                        <DatePicker
                            selected={endDate}
                            onChange={(date: Date | null) => setEndDate(date)}
                            dateFormat="dd-MM-yyyy"
                            placeholderText="DD-MM-YYYY"
                            className={styles.datePicker}
                            isClearable
                            showMonthDropdown
                            showYearDropdown
                            dropdownMode="select"
                            minDate={startDate || undefined}
                            portalId="root"
                        />
                    </div>
                    <div className={styles.filterActions}>
                        <button onClick={handleSearch} className={styles.searchBtn}>
                            Search
                        </button>
                        <button onClick={handleReset} className={styles.resetBtn}>
                            Reset
                        </button>
                    </div>
                </div>
            </div>

            <div className={styles.scrollContent}>
                {/* Results */}
                {isLoading && (
                    <div className={styles.loading}>
                        <span className={styles.spinner}></span>
                        Loading history...
                    </div>
                )}

                {isError && (
                    <div className={styles.error}>
                        ⚠️ Failed to load recognition history
                    </div>
                )}

                {data && data.logs.length === 0 && (
                    <div className={styles.empty}>
                        📭 No recognition records found
                    </div>
                )}

                {data && data.logs.length > 0 && (
                    <div className={styles.tableWrapper}>
                        <table className={styles.table}>
                            <thead>
                                <tr>
                                    <th>Student ID</th>
                                    <th>Name</th>
                                    <th>Course</th>
                                    <th>Confidence</th>
                                    <th>Date/Time</th>
                                </tr>
                            </thead>
                            <tbody>
                                {data.logs.map((log: RecognitionHistoryLog) => (
                                    <tr key={log.id}>
                                        <td className={styles.studentId}>{log.student_id}</td>
                                        <td>{log.first_name} {log.last_name}</td>
                                        <td>
                                            {log.course_name}
                                            {log.section && ` - ${log.section}`}
                                        </td>
                                        <td>
                                            <span className={`${styles.confidence} ${getConfidenceClass(log.confidence)}`}>
                                                {(log.confidence * 100).toFixed(1)}%
                                            </span>
                                        </td>
                                        <td>{formatDisplayDate(log.detection_datetime)}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            {/* Footer with Pagination */}
            {data && data.logs.length > 0 && (
                <div className={styles.footer}>
                    <div className={styles.resultCount}>
                        Showing {page * limit + 1} - {Math.min((page + 1) * limit, data.total)} of {data.total} records
                    </div>
                    
                    {totalPages > 1 && (
                        <div className={styles.pagination}>
                            <button 
                                onClick={() => setPage(p => Math.max(0, p - 1))}
                                disabled={page === 0}
                                className={styles.pageBtn}
                            >
                                ← Previous
                            </button>
                            <span className={styles.pageInfo}>
                                Page {page + 1} of {totalPages}
                            </span>
                            <button 
                                onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))}
                                disabled={page >= totalPages - 1}
                                className={styles.pageBtn}
                            >
                                Next →
                            </button>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
