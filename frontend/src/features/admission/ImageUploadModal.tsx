import { useState, useRef } from 'react';
import { uploadStudentImages } from '../../api/admission';
import { ImagePreviewOverlay } from './ImagePreviewOverlay';
import { WebcamCapture } from './WebcamCapture';
import { TrainingProgress } from './TrainingProgress';
import styles from './ImageUploadModal.module.css';

interface ImageUploadModalProps {
    admissionId: string;
    studentId: string;
    studentName: string;
    onComplete: (success: boolean) => void;
    onClose: () => void;
}

export function ImageUploadModal({ admissionId, studentId, studentName, onComplete, onClose }: ImageUploadModalProps) {
    const [images, setImages] = useState<File[]>([]);
    const [previewImage, setPreviewImage] = useState<File | null>(null);
    const [showWebcam, setShowWebcam] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [isTraining, setIsTraining] = useState(false);
    
    // 0: idle, 1: uploading
    const [processingStep, setProcessingStep] = useState(0);
    
    const fileInputRef = useRef<HTMLInputElement>(null);
    const folderInputRef = useRef<HTMLInputElement>(null);

    // Allowed image types
    const ALLOWED_EXTENSIONS = /\.(jpg|jpeg|png|webp|bmp|gif)$/i;

    const addImages = (newFiles: File[]) => {
        const validFiles: File[] = [];
        const rejected: string[] = [];
        
        for (const f of newFiles) {
            if (f.type.startsWith('image/') || ALLOWED_EXTENSIONS.test(f.name)) {
                validFiles.push(f);
            } else {
                rejected.push(f.name);
            }
        }
        
        if (rejected.length > 0) {
            setError(`Rejected ${rejected.length} non-image file(s): ${rejected.slice(0, 3).join(', ')}${rejected.length > 3 ? '...' : ''}. Only JPG, PNG, WebP, BMP, GIF allowed.`);
        }
        
        setImages(prev => [...prev, ...validFiles].slice(0, 250));
    };

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = Array.from(e.target.files || []);
        addImages(files);
        e.target.value = '';
    };

    const handleFolderSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = Array.from(e.target.files || []);
        const imageFiles = files.filter(file => 
            file.type.startsWith('image/') || 
            /\.(jpg|jpeg|png|gif|webp|bmp)$/i.test(file.name)
        );
        addImages(imageFiles);
        e.target.value = '';
    };

    const handleWebcamCapture = (file: File) => {
        addImages([file]);
    };

    const handleRemoveImage = (index: number) => {
        setImages(prev => prev.filter((_, i) => i !== index));
    };

    const handleUpload = async () => {
        if (images.length === 0) return;

        setLoading(true);
        setError('');
        setProcessingStep(1);

        try {
            // 1. Upload
            await uploadStudentImages(admissionId, images);
            
            // 2. Switch to Training UI (TrainingProgress component)
            setIsTraining(true);
            setLoading(false);
            
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to upload images');
            setLoading(false);
            setProcessingStep(0);
        }
    };

    const getProgressPercentage = () => {
        switch (processingStep) {
            case 1: return 45; // Uploading state
            default: return 0;
        }
    };

    const getStatusText = () => {
        switch (processingStep) {
            case 1: return `Uploading ${images.length} images...`;
            default: return 'Processing...';
        }
    };

    // If training started, show the TrainingProgress component instead
    if (isTraining) {
        return (
            <TrainingProgress 
                admissionId={admissionId}
                studentId={studentId}
                studentName={studentName}
                onComplete={(success) => {
                    if (success) {
                        onComplete(true);
                    }
                }}
                onClose={() => {
                    // If closed without completing, just go back to this modal or close?
                    // Usually Close means "I'm done" or "Cancel".
                    // If it was valid completion, onComplete would be called.
                    // If we are here, it might be an early close.
                    // Let's close the whole thing.
                    onClose();
                }}
            />
        );
    }

    return (
        <div className={styles.overlay}>
            <div className={styles.modal}>
                <div className={styles.header}>
                    <h3>📷 Upload Face Images</h3>
                    {!loading && <button onClick={onClose} className={styles.closeBtn}>×</button>}
                </div>

                <div className={styles.student}>
                    <span>Student: <strong>{studentName}</strong></span>
                    <span className={styles.studentId}>{studentId}</span>
                </div>

                {!loading && (
                    <>
                        <p className={styles.instructions}>
                            Upload 5-250 clear face images for recognition training.
                        </p>

                        <div className={styles.sourceButtons}>
                            <button 
                                type="button" 
                                onClick={() => setShowWebcam(true)} 
                                className={styles.sourceBtn}
                            >
                                📷 Webcam
                            </button>
                            <button 
                                type="button" 
                                onClick={() => fileInputRef.current?.click()} 
                                className={styles.sourceBtn}
                            >
                                📁 Files
                            </button>
                            <button 
                                type="button" 
                                onClick={() => folderInputRef.current?.click()} 
                                className={styles.sourceBtn}
                            >
                                📂 Folder
                            </button>
                        </div>

                        <input
                            ref={fileInputRef}
                            type="file"
                            accept="image/jpeg,image/png,image/webp,image/bmp,image/gif"
                            multiple
                            onChange={handleFileSelect}
                            style={{ display: 'none' }}
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
                            style={{ display: 'none' }}
                        />

                        {images.length > 0 ? (
                            <div className={styles.preview}>
                                <div className={styles.previewHeader}>
                                    <span>{images.length} / 250 images</span>
                                    <button 
                                        type="button" 
                                        onClick={() => setImages([])} 
                                        className={styles.clearBtn}
                                    >
                                        Clear All
                                    </button>
                                </div>
                                <div className={styles.imageGrid}>
                                    {images.map((img, i) => (
                                        <div 
                                            key={`${img.name}-${i}`} 
                                            className={styles.imageItem}
                                            onClick={() => setPreviewImage(img)}
                                            style={{ cursor: 'pointer' }}
                                        >
                                            <img src={URL.createObjectURL(img)} alt={`Face ${i + 1}`} />
                                            <button 
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    handleRemoveImage(i);
                                                }} 
                                                className={styles.removeBtn}
                                            >×</button>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ) : (
                            <div className={styles.emptyState}>
                                <span className={styles.emptyIcon}>📸</span>
                                <p>No images added yet</p>
                            </div>
                        )}
                    </>
                )}

                {loading && (
                    <div className={styles.progressContainer}>
                        <div className={styles.progressBar}>
                            <div 
                                className={styles.progressFill}
                                style={{ width: `${getProgressPercentage()}%` }}
                            />
                            <div className={styles.progressText}>
                                {getStatusText()} ({getProgressPercentage()}%)
                            </div>
                        </div>
                    </div>
                )}

                {error && <div className={styles.error}>{error}</div>}

                {!loading && (
                    <>
                         <div className={styles.actions}>
                            <button onClick={onClose} className={styles.cancelBtn}>
                                Cancel
                            </button>
                            <button 
                                onClick={handleUpload} 
                                className={styles.uploadBtn} 
                                disabled={images.length < 5}
                                title={images.length > 0 && images.length < 5 ? "Minimum 5 images required" : "Upload and start training"}
                            >
                                Upload & Train ({images.length} Images)
                            </button>
                        </div>
                        {images.length > 0 && images.length < 5 && (
                            <div className={styles.warningText}>⚠ Please upload at least 5 images</div>
                        )}
                    </>
                )}
            </div>

            {/* Webcam capture modal */}
            {showWebcam && (
                <WebcamCapture
                    onCapture={handleWebcamCapture}
                    onClose={() => setShowWebcam(false)}
                    maxCaptures={250}
                    capturedCount={images.length}
                />
            )}

            {previewImage && (
                <ImagePreviewOverlay
                    image={previewImage}
                    onClose={() => setPreviewImage(null)}
                />
            )}
        </div>
    );
}
