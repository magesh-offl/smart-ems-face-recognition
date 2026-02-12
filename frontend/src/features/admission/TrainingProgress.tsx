import { useState, useEffect, useRef } from 'react';
import { trainStudentFace } from '../../api/admission';
import styles from './TrainingProgress.module.css';

interface TrainingProgressProps {
    admissionId: string;
    studentId: string;
    studentName: string;
    onComplete?: (success: boolean) => void;
    onClose: () => void;
}

type TrainingStage = 'starting' | 'detecting' | 'extracting' | 'embedding' | 'saving' | 'complete' | 'error';

interface StageInfo {
    label: string;
    icon: string;
    description: string;
}

const STAGES: Record<TrainingStage, StageInfo> = {
    starting: { label: 'Starting', icon: '🚀', description: 'Initiating face recognition training...' },
    detecting: { label: 'Detecting Faces', icon: '🔍', description: 'Analyzing uploaded images for faces...' },
    extracting: { label: 'Extracting Features', icon: '📐', description: 'Extracting facial landmarks and features...' },
    embedding: { label: 'Creating Embeddings', icon: '🧮', description: 'Generating face recognition embeddings...' },
    saving: { label: 'Saving Model', icon: '💾', description: 'Saving trained model to database...' },
    complete: { label: 'Complete', icon: '✅', description: 'Face recognition training complete!' },
    error: { label: 'Error', icon: '❌', description: 'Training failed. Please try again.' },
};

const STAGE_ORDER: TrainingStage[] = ['starting', 'detecting', 'extracting', 'embedding', 'saving', 'complete'];

export function TrainingProgress({ admissionId, studentId, studentName, onComplete, onClose }: TrainingProgressProps) {
    const [currentStage, setCurrentStage] = useState<TrainingStage>('starting');
    const [progress, setProgress] = useState(0);
    const [error, setError] = useState<string | null>(null);
    const [facesFound, setFacesFound] = useState<number | null>(null);
    const [isTraining, setIsTraining] = useState(false);
    const animationRef = useRef<ReturnType<typeof setInterval> | null>(null);
    const trainingStartedRef = useRef(false);

    useEffect(() => {
        // Start training when component mounts
        if (!trainingStartedRef.current) {
            trainingStartedRef.current = true;
            startRealTraining();
        }

        return () => {
            // Cleanup animation on unmount
            if (animationRef.current) {
                clearInterval(animationRef.current);
            }
        };
    }, []);

    const startRealTraining = async () => {
        setIsTraining(true);
        setError(null);
        setCurrentStage('starting');
        setProgress(0);

        // Start progress animation (will run concurrently with API call)
        startProgressAnimation();

        try {
            // Call the actual backend API - this is synchronous and waits for completion
            const result = await trainStudentFace(admissionId);
            
            // Stop animation
            if (animationRef.current) {
                clearInterval(animationRef.current);
            }

            // Process result
            if (result.is_trained) {
                setCurrentStage('complete');
                setProgress(100);
                setFacesFound(result.faces_detected || 0);
                onComplete?.(true);
            } else {
                setCurrentStage('error');
                setError(result.message || 'Training failed');
                onComplete?.(false);
            }
        } catch (err: any) {
            // Stop animation
            if (animationRef.current) {
                clearInterval(animationRef.current);
            }
            
            setCurrentStage('error');
            setError(err.response?.data?.detail || err.message || 'Training failed');
            onComplete?.(false);
        } finally {
            setIsTraining(false);
        }
    };

    // Animate progress while waiting for backend
    const startProgressAnimation = () => {
        const stages: TrainingStage[] = ['detecting', 'extracting', 'embedding', 'saving'];
        let currentStageIndex = 0;
        let currentProgress = 0;

        animationRef.current = setInterval(() => {
            // Move through stages slowly
            currentProgress += 2;
            
            if (currentProgress >= 95) {
                // Cap at 95% until real completion
                currentProgress = 95;
            }
            
            // Calculate which stage we should show based on progress
            const stageThreshold = 100 / stages.length;
            const newStageIndex = Math.min(
                Math.floor(currentProgress / stageThreshold),
                stages.length - 1
            );
            
            if (newStageIndex !== currentStageIndex) {
                currentStageIndex = newStageIndex;
                setCurrentStage(stages[currentStageIndex]);
            }
            
            setProgress(currentProgress);
        }, 200); // Update every 200ms
    };

    const handleRetry = () => {
        trainingStartedRef.current = false;
        setCurrentStage('starting');
        setProgress(0);
        setError(null);
        startRealTraining();
    };

    const stageIndex = STAGE_ORDER.indexOf(currentStage);
    const isComplete = currentStage === 'complete';
    const hasError = currentStage === 'error';
    const currentStageInfo = STAGES[currentStage];

    return (
        <div className={styles.overlay}>
            <div className={styles.modal}>
                <div className={styles.header}>
                    <h3>🎓 Training Face Recognition</h3>
                    {(isComplete || hasError) && (
                        <button onClick={onClose} className={styles.closeBtn}>×</button>
                    )}
                </div>

                <div className={styles.student}>
                    <span>Student: <strong>{studentName}</strong></span>
                    <span className={styles.studentId}>{studentId}</span>
                </div>

                {/* Stage indicators */}
                <div className={styles.stages}>
                    {STAGE_ORDER.slice(1, 5).map((stage, i) => {
                        const displayIndex = i + 1; // Offset for 'starting'
                        const isCurrentStage = stage === currentStage;
                        const isPastStage = stageIndex > displayIndex;
                        const isFutureStage = stageIndex < displayIndex;
                        
                        return (
                            <div 
                                key={stage} 
                                className={`${styles.stageIndicator} ${isPastStage ? styles.complete : ''} ${isCurrentStage ? styles.active : ''} ${isFutureStage ? styles.pending : ''}`}
                            >
                                <div className={styles.stageCircle}>
                                    {isPastStage ? '✓' : i + 1}
                                </div>
                                <span className={styles.stageLabel}>{STAGES[stage].label}</span>
                            </div>
                        );
                    })}
                </div>

                {/* Current stage display */}
                <div className={`${styles.currentStage} ${isComplete ? styles.success : ''} ${hasError ? styles.error : ''}`}>
                    <span className={styles.stageIcon}>{currentStageInfo.icon}</span>
                    <div className={styles.stageInfo}>
                        <h4>{currentStageInfo.label}</h4>
                        <p>{currentStageInfo.description}</p>
                    </div>
                </div>

                {/* Face Scanner Animation */}
                {!isComplete && !hasError && (
                    <div className={styles.faceScannerContainer}>
                        <div className={styles.faceScanner}>
                            <svg className={styles.faceOutline} viewBox="0 0 100 120" fill="none">
                                {/* Face outline */}
                                <ellipse cx="50" cy="55" rx="35" ry="45" stroke="currentColor" strokeWidth="2" />
                                {/* Eyes */}
                                <ellipse cx="35" cy="45" rx="6" ry="4" className={styles.faceFeature} />
                                <ellipse cx="65" cy="45" rx="6" ry="4" className={styles.faceFeature} />
                                {/* Nose */}
                                <path d="M50 50 L50 65 L45 70" stroke="currentColor" strokeWidth="1.5" fill="none" className={styles.faceFeature} />
                                {/* Mouth */}
                                <path d="M38 80 Q50 90 62 80" stroke="currentColor" strokeWidth="1.5" fill="none" className={styles.faceFeature} />
                                {/* Feature points */}
                                <circle cx="35" cy="45" r="2" className={styles.featurePoint} style={{'--delay': '0s'} as React.CSSProperties} />
                                <circle cx="65" cy="45" r="2" className={styles.featurePoint} style={{'--delay': '0.2s'} as React.CSSProperties} />
                                <circle cx="50" cy="35" r="2" className={styles.featurePoint} style={{'--delay': '0.4s'} as React.CSSProperties} />
                                <circle cx="50" cy="65" r="2" className={styles.featurePoint} style={{'--delay': '0.6s'} as React.CSSProperties} />
                                <circle cx="50" cy="80" r="2" className={styles.featurePoint} style={{'--delay': '0.8s'} as React.CSSProperties} />
                                <circle cx="25" cy="55" r="2" className={styles.featurePoint} style={{'--delay': '1s'} as React.CSSProperties} />
                                <circle cx="75" cy="55" r="2" className={styles.featurePoint} style={{'--delay': '1.2s'} as React.CSSProperties} />
                            </svg>
                            <div className={styles.scanLine}></div>
                        </div>
                    </div>
                )}

                {/* Progress bar */}
                {!isComplete && !hasError && (
                    <div className={styles.progressContainer}>
                        <div 
                            className={styles.progressBar} 
                            style={{ width: `${progress}%` }}
                        />
                        <span className={styles.progressText}>
                            {isTraining ? 'Processing...' : `${Math.round(progress)}%`}
                        </span>
                    </div>
                )}

                {/* Results */}
                {facesFound !== null && isComplete && (
                    <div className={styles.results}>
                        <div className={styles.resultItem}>
                            <span className={styles.resultIcon}>👤</span>
                            <span>{facesFound} face{facesFound !== 1 ? 's' : ''} processed</span>
                        </div>
                        <div className={styles.resultItem}>
                            <span className={styles.resultIcon}>✓</span>
                            <span>Model saved successfully</span>
                        </div>
                    </div>
                )}

                {/* Error display */}
                {error && (
                    <div className={styles.errorMessage}>
                        {error}
                    </div>
                )}

                {/* Actions */}
                <div className={styles.actions}>
                    {isComplete && (
                        <button onClick={onClose} className={styles.doneBtn}>
                            Done
                        </button>
                    )}
                    {hasError && (
                        <>
                            <button onClick={onClose} className={styles.cancelBtn}>
                                Cancel
                            </button>
                            <button onClick={handleRetry} className={styles.retryBtn}>
                                Retry
                            </button>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
}
