import { useState } from 'react';
import { GroupRecognition, RecognitionHistory } from '../features/recognition';
import styles from './RecognitionPage.module.css';

type Tab = 'upload' | 'history';

export function RecognitionPage() {
    const [activeTab, setActiveTab] = useState<Tab>('upload');
    const [isRecognitionProcessing, setIsRecognitionProcessing] = useState(false);

    return (
        <div className={styles.container}>
            {/* Tab Navigation */}
            <div className={styles.tabs}>
                <button
                    className={`${styles.tab} ${activeTab === 'upload' ? styles.active : ''}`}
                    onClick={() => setActiveTab('upload')}
                >
                    📸 Upload & Recognize
                </button>
                <button
                    className={`${styles.tab} ${activeTab === 'history' ? styles.active : ''}`}
                    onClick={() => setActiveTab('history')}
                    disabled={isRecognitionProcessing && activeTab === 'upload'}
                    style={{ opacity: isRecognitionProcessing && activeTab === 'upload' ? 0.5 : 1, cursor: isRecognitionProcessing && activeTab === 'upload' ? 'not-allowed' : 'pointer' }}
                    title={isRecognitionProcessing ? 'Cannot switch tabs while processing' : ''}
                >
                    📋 History
                </button>
            </div>

            {/* Tab Content */}
            <div className={styles.content}>
                {activeTab === 'upload' && (
                    <GroupRecognition 
                        onProcessingChange={setIsRecognitionProcessing}
                    />
                )}
                {activeTab === 'history' && <RecognitionHistory />}
            </div>
        </div>
    );
}
