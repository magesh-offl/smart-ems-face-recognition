import { useState } from 'react';
import { StudentList, StudentAdmitForm } from '../features/admission';
import styles from './AdmissionPage.module.css';

type Tab = 'students' | 'admit';

export function AdmissionPage() {
    const [activeTab, setActiveTab] = useState<Tab>('students');

    const handleAdmitComplete = () => {
        setActiveTab('students');
    };

    return (
        <div className={styles.container}>
            <div className={styles.content}>
                {activeTab === 'students' && (
                    <StudentList onAdmitClick={() => setActiveTab('admit')} />
                )}
                {activeTab === 'admit' && (
                    <StudentAdmitForm 
                        onSuccess={handleAdmitComplete} 
                        onCancel={() => setActiveTab('students')} 
                    />
                )}
            </div>
        </div>
    );
}

