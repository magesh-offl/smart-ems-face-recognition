import { useState, type ReactNode } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../features/auth';
import { ROUTES } from '../config';
import { Home, Camera, Users, Settings, LogOut, Menu, ChevronLeft } from 'lucide-react';
import styles from './DashboardLayout.module.css';

interface DashboardLayoutProps {
    children: ReactNode;
}

interface NavItem {
    path: string;
    icon: typeof Home;
    label: string;
    adminOnly?: boolean;
}

const navItems: NavItem[] = [
    { path: ROUTES.DASHBOARD, icon: Home, label: 'Dashboard' },
    { path: ROUTES.ADMISSION, icon: Settings, label: 'Admission', adminOnly: true },
    { path: ROUTES.RECOGNITION, icon: Camera, label: 'Recognition' },
    { path: ROUTES.PERSONS, icon: Users, label: 'Persons' },
];

export function DashboardLayout({ children }: DashboardLayoutProps) {
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);
    const location = useLocation();
    const navigate = useNavigate();
    const { logout, isAdmin } = useAuth();

    const visibleNavItems = navItems.filter(item => !item.adminOnly || isAdmin);

    const handleLogout = () => {
        logout();
        navigate(ROUTES.LOGIN);
    };

    return (
        <div className={`${styles.container} ${isSidebarOpen ? styles.sidebarOpen : styles.sidebarClosed}`}>
            <aside className={`${styles.sidebar} ${isSidebarOpen ? styles.open : styles.closed}`}>
                <div className={styles.logo}>
                    <span className={styles.logoIcon}>🎓</span>
                    {isSidebarOpen && <span className={styles.logoText}>Smart EMS</span>}
                </div>

                <nav className={styles.nav}>
                    {visibleNavItems.map(({ path, icon: Icon, label }) => (
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

                <button className={styles.logoutBtn} onClick={handleLogout}>
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
                        {isSidebarOpen ? <ChevronLeft size={20} /> : <Menu size={20} />}
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
