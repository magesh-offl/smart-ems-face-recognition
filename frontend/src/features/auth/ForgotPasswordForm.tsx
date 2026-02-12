import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from './useAuth';
import { ROUTES } from '../../config';
import styles from './LoginForm.module.css';

export function ForgotPasswordForm() {
    const [username, setUsername] = useState('');
    const [submitted, setSubmitted] = useState(false);
    const [message, setMessage] = useState('');
    const { forgotPassword, isLoading, error } = useAuth();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!username.trim()) return;
        
        try {
            const result = await forgotPassword(username);
            setMessage(result.message);
            setSubmitted(true);
        } catch {
            // Error is handled by useAuth
        }
    };

    if (submitted) {
        return (
            <div className={styles.form}>
                <h2 className={styles.title}>Request Submitted</h2>
                <p className={styles.message}>{message}</p>
                <p className={styles.info}>
                    An administrator will review your request and contact you with your new password.
                </p>
                <Link to={ROUTES.LOGIN} className={styles.link}>
                    Back to Login
                </Link>
            </div>
        );
    }

    return (
        <form onSubmit={handleSubmit} className={styles.form}>
            <h2 className={styles.title}>Forgot Password</h2>
            <p className={styles.info}>
                Enter your username to request a password reset. An administrator will review your request.
            </p>
            
            {error && <div className={styles.error}>{error}</div>}
            
            <div className={styles.inputGroup}>
                <label htmlFor="username" className={styles.label}>Username</label>
                <input
                    id="username"
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className={styles.input}
                    placeholder="Enter your username"
                    required
                    autoFocus
                />
            </div>
            
            <button 
                type="submit" 
                className={styles.button}
                disabled={isLoading}
            >
                {isLoading ? 'Submitting...' : 'Submit Request'}
            </button>
            
            <Link to={ROUTES.LOGIN} className={styles.link}>
                Back to Login
            </Link>
        </form>
    );
}
