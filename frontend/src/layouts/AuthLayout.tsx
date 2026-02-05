import { ReactNode } from 'react';
import styles from './AuthLayout.module.css';

interface AuthLayoutProps {
    children: ReactNode;
}

export function AuthLayout({ children }: AuthLayoutProps) {
    return (
        <div className={styles.container}>
            <div className={styles.background} />
            <main className={styles.content}>
                {children}
            </main>
        </div>
    );
}
