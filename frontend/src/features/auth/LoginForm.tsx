import { useState, type FormEvent } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from './useAuth';
import { ROUTES } from '../../config';
import styles from './LoginForm.module.css';

export function LoginForm() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const { login, isLoading, error } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();
        const success = await login({ username, password });
        if (success) {
            navigate(ROUTES.DASHBOARD);
        }
    };

    return (
        <form className={styles.form} onSubmit={handleSubmit}>
            <h1 className={styles.title}>Smart EMS</h1>
            <p className={styles.subtitle}>Education Management System</p>

            {error && <div className={styles.error}>{error}</div>}

            <div className={styles.inputGroup}>
                <label htmlFor="username">Username</label>
                <input
                    id="username"
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="Enter username"
                    required
                    disabled={isLoading}
                />
            </div>

            <div className={styles.inputGroup}>
                <label htmlFor="password">Password</label>
                <input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter password"
                    required
                    disabled={isLoading}
                />
            </div>

            <button type="submit" className={styles.button} disabled={isLoading}>
                {isLoading ? 'Logging in...' : 'Log In'}
            </button>

            <Link to={ROUTES.FORGOT_PASSWORD} className={styles.link}>
                Forgot Password?
            </Link>
        </form>
    );
}

