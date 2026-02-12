import { useState, useRef, useCallback } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { recognizeGroup } from '../../api/recognition';
import type { GroupRecognitionResult } from '../../api/recognition';
import { WebcamCapture } from '../admission/WebcamCapture';
import { ImagePreviewOverlay } from '../admission/ImagePreviewOverlay';
import styles from './GroupRecognition.module.css';

interface ImageResult {
    file: File;
    previewUrl: string;
    result: GroupRecognitionResult | null;
    error: string | null;
    status: 'pending' | 'processing' | 'done' | 'error';
}

interface GroupRecognitionProps {
    onProcessingChange?: (isProcessing: boolean) => void;
}

export function GroupRecognition({ onProcessingChange }: GroupRecognitionProps) {
    const [imageItems, setImageItems] = useState<ImageResult[]>([]);
    const [results, setResults] = useState<ImageResult[]>([]);
    const [isProcessing, setIsProcessing] = useState(false);
    const [processingIndex, setProcessingIndex] = useState(-1);
    const [showWebcam, setShowWebcam] = useState(false);
    const [previewImage, setPreviewImage] = useState<File | null>(null);
    const [expandedResults, setExpandedResults] = useState<Set<number>>(new Set());
    const fileInputRef = useRef<HTMLInputElement>(null);
    const folderInputRef = useRef<HTMLInputElement>(null);
    const queryClient = useQueryClient();

    const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/bmp', 'image/gif'];

    const addImages = useCallback((files: File[]) => {
        const validFiles = files.filter(f =>
            f.type.startsWith('image/') || ALLOWED_TYPES.some(t => f.type === t) ||
            /\.(jpg|jpeg|png|webp|bmp|gif)$/i.test(f.name)
        );

        if (validFiles.length === 0) return;

        const newItems: ImageResult[] = validFiles.map(file => ({
            file,
            previewUrl: URL.createObjectURL(file),
            result: null,
            error: null,
            status: 'pending' as const,
        }));

        setImageItems(prev => [...prev, ...newItems]);
    }, []);

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = Array.from(e.target.files || []);
        addImages(files);
        e.target.value = '';
    };

    const handleFolderSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = Array.from(e.target.files || []);
        addImages(files);
        e.target.value = '';
    };

    const handleWebcamCapture = useCallback((file: File) => {
        addImages([file]);
    }, [addImages]);

    const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        const files = Array.from(e.dataTransfer.files).filter(f => f.type.startsWith('image/'));
        addImages(files);
    };

    const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
    };

    const removeImage = (index: number) => {
        setImageItems(prev => {
            const item = prev[index];
            if (item) URL.revokeObjectURL(item.previewUrl);
            return prev.filter((_, i) => i !== index);
        });
    };

    const clearAll = () => {
        imageItems.forEach(item => URL.revokeObjectURL(item.previewUrl));
        results.forEach(item => URL.revokeObjectURL(item.previewUrl));
        setImageItems([]);
        setResults([]);
        setExpandedResults(new Set());
    };

    const handleRecognizeAll = async () => {
        if (imageItems.length === 0) return;

        setIsProcessing(true);
        onProcessingChange?.(true);
        const allExpanded = new Set<number>();
        
        // Use a local copy to track updates during processing to avoid stale state issues
        let currentItems = [...imageItems];
        const successfulItems: ImageResult[] = [];

        for (let i = 0; i < currentItems.length; i++) {
            if (currentItems[i].status === 'done') continue;

            setProcessingIndex(i);

            // Mark current as processing in UI
            currentItems[i] = { ...currentItems[i], status: 'processing' };
            setImageItems([...currentItems]);

            try {
                const response = await recognizeGroup(currentItems[i].file);
                // Update local item
                currentItems[i] = { 
                    ...currentItems[i], 
                    result: response, 
                    status: 'done', 
                    error: null 
                };
                successfulItems.push(currentItems[i]);
            } catch (err: any) {
                let message = err.response?.data?.detail || err.message || 'Recognition failed';
                
                // Handle 404 as "No faces detected" and treat as a result
                if (err.response?.status === 404) {
                    message = 'No faces detected';
                }

                currentItems[i] = { 
                    ...currentItems[i], 
                    error: message, 
                    status: 'error' 
                };
                
                // Add to processed items so it moves to results list
                successfulItems.push(currentItems[i]);
            }
            
            // Update UI with result
            setImageItems([...currentItems]);
        }

        setExpandedResults(allExpanded);
        
        // Move processed items to results state
        if (successfulItems.length > 0) {
            setResults(prev => [...prev, ...successfulItems]);
            // Remove processed items (success or error) from the upload grid
            setImageItems(currentItems.filter(item => !successfulItems.includes(item)));
        } else {
            // Should not happen if everything is moved, but safe fallback
            setImageItems(currentItems);
        }

        setIsProcessing(false);
        onProcessingChange?.(false);
        setProcessingIndex(-1);

        // Refresh history tab
        queryClient.invalidateQueries({ queryKey: ['recognitionHistory'] });
    };

    const toggleResult = (index: number) => {
        setExpandedResults(prev => {
            const next = new Set(prev);
            if (next.has(index)) next.delete(index);
            else next.add(index);
            return next;
        });
    };

    const getConfidenceClass = (confidence: number): string => {
        if (confidence >= 0.8) return styles.highConfidence;
        if (confidence >= 0.6) return styles.mediumConfidence;
        return styles.lowConfidence;
    };

    const hasResults = imageItems.some(item => item.result || item.error);
    const hasCompletedResults = results.length > 0;
    const isInputDisabled = isProcessing || hasCompletedResults;

    const pendingCount = imageItems.filter(i => i.status === 'pending').length;
    const doneCount = imageItems.filter(i => i.status === 'done').length;
    const errorCount = imageItems.filter(i => i.status === 'error').length;

    return (
        <div className={styles.container}>
            <div className={styles.fixedHeader}>
                <h2 className={styles.title}>🎯 Group Face Recognition</h2>
                <p className={styles.subtitle}>
                    Upload group photos to identify registered students
                </p>

                {/* Source Buttons */}
                <div className={styles.sourceButtons}>
                    <button
                        type="button"
                        onClick={() => setShowWebcam(true)}
                        className={styles.sourceBtn}
                        disabled={isInputDisabled}
                    >
                        📷 Webcam
                    </button>
                    <button
                        type="button"
                        onClick={() => fileInputRef.current?.click()}
                        className={styles.sourceBtn}
                        disabled={isInputDisabled}
                    >
                        📁 Files
                    </button>
                    <button
                        type="button"
                        onClick={() => folderInputRef.current?.click()}
                        className={styles.sourceBtn}
                        disabled={isInputDisabled}
                    >
                        📂 Folder
                    </button>
                </div>
            </div>

            <div className={styles.scrollContent}>
                {/* Drag & Drop Area (shown when no images yet and no results) */}
                {imageItems.length === 0 && !hasCompletedResults && (
                    <div
                        className={styles.uploadArea}
                        onClick={() => fileInputRef.current?.click()}
                        onDrop={handleDrop}
                        onDragOver={handleDragOver}
                    >
                        <div className={styles.uploadIcon}>📸</div>
                        <p className={styles.uploadText}>
                            Drop group photos here or click to browse
                        </p>
                        <p className={styles.uploadHint}>
                            Supports JPEG, PNG, WebP • Multiple images allowed
                        </p>
                    </div>
                )}

                {/* Hidden file inputs */}
                <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/jpeg,image/png,image/webp,image/bmp,image/gif"
                    multiple
                    onChange={handleFileSelect}
                    className={styles.hiddenInput}
                />
                <input
                    ref={folderInputRef}
                    type="file"
                    accept="image/jpeg,image/png,image/webp,image/bmp,image/gif"
                    // @ts-ignore
                    webkitdirectory=""
                    // @ts-ignore
                    directory=""
                    multiple
                    onChange={handleFolderSelect}
                    className={styles.hiddenInput}
                />

                {/* Image Preview Grid */}
                {imageItems.length > 0 && (
                    <div className={styles.previewSection}>
                        <div className={styles.previewHeader}>
                            <span className={styles.imageCount}>
                                {imageItems.length} image{imageItems.length !== 1 ? 's' : ''} selected
                            </span>
                            <div className={styles.previewHeaderActions}>
                                {!isProcessing && (
                                    <button
                                        onClick={clearAll}
                                        className={styles.clearAllBtn}
                                    >
                                        ✕ Clear All
                                    </button>
                                )}
                            </div>
                        </div>

                        {/* Drop zone to add more */}
                        <div
                            className={styles.previewGrid}
                            onDrop={handleDrop}
                            onDragOver={handleDragOver}
                        >
                            {imageItems.map((item, index) => (
                                <div
                                    key={index}
                                    className={`${styles.thumbCard} ${styles[item.status]}`}
                                    onClick={() => setPreviewImage(item.file)}
                                    style={{ cursor: 'pointer' }}
                                >
                                    <img
                                        src={item.previewUrl}
                                        alt={item.file.name}
                                        className={styles.thumbImg}
                                    />
                                    {item.status === 'processing' && (
                                        <div className={styles.thumbOverlay}>
                                            <span className={styles.thumbSpinner}></span>
                                        </div>
                                    )}
                                    {item.status === 'done' && (
                                        <div className={styles.thumbBadge}>✓</div>
                                    )}
                                    {item.status === 'error' && (
                                        <div className={`${styles.thumbBadge} ${styles.thumbBadgeError}`}>!</div>
                                    )}
                                    {!isProcessing && (
                                        <button
                                            className={styles.thumbRemove}
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                removeImage(index);
                                            }}
                                            title="Remove"
                                        >
                                            ×
                                        </button>
                                    )}
                                </div>
                            ))}

                            {/* Add more button */}
                            {!isProcessing && (
                                <button
                                    className={styles.addMoreBtn}
                                    onClick={() => fileInputRef.current?.click()}
                                    title="Add more images"
                                >
                                    + Add
                                </button>
                            )}
                        </div>

                        {/* Progress Bar */}
                        {isProcessing && (
                            <div className={styles.progressSection}>
                                <div className={styles.progressBar}>
                                    <div
                                        className={styles.progressFill}
                                        style={{ width: `${((processingIndex + 1) / imageItems.length) * 100}%` }}
                                    />
                                </div>
                                <span className={styles.progressText}>
                                    Processing image {processingIndex + 1} / {imageItems.length}...
                                </span>
                            </div>
                        )}

                        {/* Action Buttons */}
                        <div className={styles.actionBar}>
                            {!isProcessing && pendingCount > 0 && (
                                <button
                                    onClick={handleRecognizeAll}
                                    className={styles.analyzeBtn}
                                >
                                    🔍 Recognize {imageItems.length > 1 ? `(${imageItems.length} images)` : ''}
                                </button>
                            )}
                            {!isProcessing && hasResults && (
                                <div className={styles.summaryBadges}>
                                    {doneCount > 0 && (
                                        <span className={styles.doneBadge}>✓ {doneCount} processed</span>
                                    )}
                                    {errorCount > 0 && (
                                        <span className={styles.errorBadge}>⚠ {errorCount} failed</span>
                                    )}
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* Grouped Results */}
                {(results.length > 0 || hasResults) && (
                    <div className={styles.results}>
                        <div className={styles.resultsHeader}>
                            <h3 className={styles.resultsTitle}>📊 Recognition Results</h3>
                            {hasCompletedResults && (
                                <button onClick={clearAll} className={styles.clearAllBtn}>
                                    ✕ Clear Results
                                </button>
                            )}
                        </div>

                        {[...results, ...imageItems.filter(i => i.status === 'done' || i.result)].map((item, index) => {
                            if (!item.result && !item.error) return null;
                            const isExpanded = expandedResults.has(index);
                            const r = item.result;

                            return (
                                <div key={index} className={styles.resultGroup}>
                                    <button
                                        className={styles.resultGroupHeader}
                                        onClick={() => toggleResult(index)}
                                    >
                                        <div className={styles.resultGroupTitle}>
                                            <img
                                                src={item.previewUrl}
                                                alt=""
                                                className={styles.resultThumb}
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    setPreviewImage(item.file);
                                                }}
                                                style={{ cursor: 'zoom-in' }}
                                            />
                                            <div className={styles.resultGroupInfo}>
                                                <span className={styles.resultFileName}>
                                                    📷 Image {index + 1}
                                                    <span className={styles.resultFileNameSub}> ({item.file.name})</span>
                                                </span>
                                                {r && (
                                                    <span className={styles.resultSummary}>
                                                        {r.stats.total_faces_detected} faces • {' '}
                                                        <span className={styles.recognized}>{r.stats.recognized_count} recognized</span> • {' '}
                                                        <span className={styles.unknown}>{r.stats.unknown_count} unknown</span>
                                                    </span>
                                                )}
                                                {item.error && (
                                                    <span className={styles.resultError}>⚠️ {item.error}</span>
                                                )}
                                            </div>
                                        </div>
                                        <span className={styles.expandIcon}>{isExpanded ? '▼' : '▶'}</span>
                                    </button>

                                    {isExpanded && r && (
                                        <div className={styles.resultGroupBody}>
                                            {/* Stats */}
                                            <div className={styles.statsBar}>
                                                <div className={styles.stat}>
                                                    <span className={styles.statValue}>{r.stats.total_faces_detected}</span>
                                                    <span className={styles.statLabel}>Faces</span>
                                                </div>
                                                <div className={styles.stat}>
                                                    <span className={`${styles.statValue} ${styles.recognized}`}>
                                                        {r.stats.recognized_count}
                                                    </span>
                                                    <span className={styles.statLabel}>Recognized</span>
                                                </div>
                                                <div className={styles.stat}>
                                                    <span className={`${styles.statValue} ${styles.unknown}`}>
                                                        {r.stats.unknown_count}
                                                    </span>
                                                    <span className={styles.statLabel}>Unknown</span>
                                                </div>
                                                <div className={styles.stat}>
                                                    <span className={styles.statValue}>
                                                        {(r.stats.processing_time_ms / 1000).toFixed(2)}s
                                                    </span>
                                                    <span className={styles.statLabel}>Time</span>
                                                </div>
                                            </div>

                                            {/* Recognized Students */}
                                            {r.recognized.length > 0 && (
                                                <div className={styles.studentsSection}>
                                                    <h4 className={styles.sectionTitle}>✅ Recognized Students</h4>
                                                    <div className={styles.studentsGrid}>
                                                        {r.recognized.map((student, sIdx) => (
                                                            <div key={sIdx} className={styles.studentCard}>
                                                                <div className={styles.studentHeader}>
                                                                    <span className={styles.studentId}>{student.student_id}</span>
                                                                    <span className={`${styles.confidence} ${getConfidenceClass(student.confidence)}`}>
                                                                        {(student.confidence * 100).toFixed(1)}%
                                                                    </span>
                                                                </div>
                                                                <div className={styles.studentName}>
                                                                    {student.first_name} {student.last_name}
                                                                </div>
                                                                <div className={styles.studentDetails}>
                                                                    <span className={styles.courseBadge}>
                                                                        {student.course_name} {student.section && `- ${student.section}`}
                                                                    </span>
                                                                </div>
                                                            </div>
                                                        ))}
                                                    </div>
                                                </div>
                                            )}

                                            {/* Unknown Faces */}
                                            {r.stats.unknown_count > 0 && (
                                                <div className={styles.unknownSection}>
                                                    <h4 className={styles.sectionTitle}>❓ Unknown Faces</h4>
                                                    <p className={styles.unknownText}>
                                                        {r.stats.unknown_count} face(s) could not be matched to any registered student.
                                                    </p>
                                                </div>
                                            )}
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>

            {/* Webcam Modal */}
            {showWebcam && (
                <WebcamCapture
                    onCapture={handleWebcamCapture}
                    onClose={() => setShowWebcam(false)}
                    maxCaptures={50}
                    capturedCount={imageItems.length}
                />
            )}

            {/* Image Preview Overlay */}
            {previewImage && (
                <ImagePreviewOverlay
                    image={previewImage}
                    onClose={() => setPreviewImage(null)}
                />
            )}
        </div>
    );
}
