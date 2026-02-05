import styles from './DashboardPage.module.css';

export function DashboardPage() {
    return (
        <div className={styles.container}>
            <div className={styles.statsGrid}>
                <div className={styles.statCard}>
                    <span className={styles.statIcon}>👥</span>
                    <div className={styles.statInfo}>
                        <span className={styles.statValue}>24</span>
                        <span className={styles.statLabel}>Known Persons</span>
                    </div>
                </div>

                <div className={styles.statCard}>
                    <span className={styles.statIcon}>📸</span>
                    <div className={styles.statInfo}>
                        <span className={styles.statValue}>156</span>
                        <span className={styles.statLabel}>Recognitions Today</span>
                    </div>
                </div>

                <div className={styles.statCard}>
                    <span className={styles.statIcon}>✅</span>
                    <div className={styles.statInfo}>
                        <span className={styles.statValue}>94%</span>
                        <span className={styles.statLabel}>Accuracy Rate</span>
                    </div>
                </div>

                <div className={styles.statCard}>
                    <span className={styles.statIcon}>🎯</span>
                    <div className={styles.statInfo}>
                        <span className={styles.statValue}>12</span>
                        <span className={styles.statLabel}>Batches Processed</span>
                    </div>
                </div>
            </div>

            <div className={styles.section}>
                <h2 className={styles.sectionTitle}>Recent Activity</h2>
                <p className={styles.emptyState}>Recognition logs will appear here...</p>
            </div>
        </div>
    );
}
