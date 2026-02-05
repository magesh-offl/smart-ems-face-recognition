import { ReactNode, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../features/auth';
import { ROUTES } from '../config';
import { Home, Camera, Users, LogOut, Menu, X } from 'lucide-react';
import styles from './DashboardLayout.module.css';

interface DashboardLayoutProps {
    children: ReactNode;
}

const navItems = [
    { path: ROUTES.DASHBOARD, icon: Home, label: 'Dashboard' },
    { path: ROUTES.RECOGNITION, icon: Camera, label: 'Recognition' },
    { path: ROUTES.PERSONS, icon: Users, label: 'Persons' },
];

export function DashboardLayout({ children }: DashboardLayoutProps) {
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);
    const location = useLocation();
    const { logout } = useAuth();

    return (
        <div className={styles.container}>
            <aside className={`${styles.sidebar} ${isSidebarOpen ? styles.open : styles.closed}`}>
                <div className={styles.logo}>
                    <span className={styles.logoIcon}>🎓</span>
                    {isSidebarOpen && <span className={styles.logoText}>Smart EMS</span>}
                </div>

                <nav className={styles.nav}>
                    {navItems.map(({ path, icon: Icon, label }) => (
                        <Link
                            key={path}
                            to={path}
                            className={`${styles.navItem} ${location.pathname === path ? styles.active : ''}`}
                        >
                            <Icon size={20} />
                            {isSidebarOpen && <span>{label}</span>}
                        </Link>
                    ))}
                </nav>

                <button className={styles.logoutBtn} onClick={logout}>
                    <LogOut size={20} />
                    {isSidebarOpen && <span>Logout</span>}
                </button>
            </aside>

            <div className={styles.main}>
                <header className={styles.header}>
                    <button
                        className={styles.menuBtn}
                        onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                    >
                        {isSidebarOpen ? <X size={20} /> : <Menu size={20} />}
                    </button>
                    <h1 className={styles.pageTitle}>
                        {navItems.find(item => item.path === location.pathname)?.label || 'Dashboard'}
                    </h1>
                </header>

                <main className={styles.content}>
                    {children}
                </main>
            </div>
        </div>
    );
}
