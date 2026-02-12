import { useState, useEffect, useRef } from 'react';
import { getPasswordResets, completePasswordReset, type PasswordResetRequest } from '../../api/admission';
import styles from './PasswordResets.module.css';

export function PasswordResets() {
    const [resets, setResets] = useState<PasswordResetRequest[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [processing, setProcessing] = useState<string | null>(null);
    const completedIdsRef = useRef<Set<string>>(new Set());  // Idempotency: track completed resets

    useEffect(() => {
        loadResets();
    }, []);

    const loadResets = async () => {
        try {
            setLoading(true);
            const data = await getPasswordResets();
            setResets(data.requests);
            setError('');
        } catch (err) {
            setError('Failed to load password reset requests');
        } finally {
            setLoading(false);
        }
    };

    const handleComplete = async (requestId: string, username: string, newPassword: string) => {
        // Idempotency: Block if already completed in this session
        if (completedIdsRef.current.has(requestId)) return;
        
        if (!confirm(`Complete password reset for ${username}?\n\nNew password: ${newPassword}\n\nMake sure you have communicated this to the user.`)) {
            return;
        }
        
        try {
            setProcessing(requestId);
            await completePasswordReset(requestId);
            completedIdsRef.current.add(requestId);
            await loadResets();
        } catch (err) {
            setError('Failed to complete password reset');
        } finally {
            setProcessing(null);
        }
    };

    if (loading) {
        return <div className={styles.loading}>Loading password reset requests...</div>;
    }

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <h2>Password Reset Requests</h2>
                <button onClick={loadResets} className={styles.refreshBtn}>
                    ↻ Refresh
                </button>
            </div>

            {error && <div className={styles.error}>{error}</div>}

            {resets.length === 0 ? (
                <div className={styles.empty}>
                    <p>No pending password reset requests</p>
                </div>
            ) : (
                <div className={styles.table}>
                    <div className={styles.tableHeader}>
                        <span>User</span>
                        <span>Role</span>
                        <span>New Password</span>
                        <span>Requested</span>
                        <span>Action</span>
                    </div>
                    {resets.map((request) => (
                        <div key={request.id} className={styles.tableRow}>
                            <span className={styles.username}>
                                {request.username}
                                <small>{request.user_id}</small>
                            </span>
                            <span className={styles.role}>{request.role_name}</span>
                            <span className={styles.password}>
                                <code>{request.new_password}</code>
                            </span>
                            <span className={styles.date}>
                                {new Date(request.created_at).toLocaleDateString()}
                            </span>
                            <span>
                                <button
                                    onClick={() => handleComplete(request.id, request.username, request.new_password)}
                                    disabled={processing === request.id}
                                    className={styles.completeBtn}
                                >
                                    {processing === request.id ? 'Processing...' : 'Complete'}
                                </button>
                            </span>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
