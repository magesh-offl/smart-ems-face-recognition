import { useState, useEffect, useRef, type FormEvent } from 'react';
import { getCourses, admitStudent, uploadStudentImages, trainStudentFace, checkGuardianPhone, type Course } from '../../api/admission';
import { WebcamCapture } from './WebcamCapture';
import { ImagePreviewOverlay } from './ImagePreviewOverlay';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import { format } from 'date-fns';
import { maskDateInput } from '../../utils/dateHelpers';
import styles from './StudentAdmitForm.module.css';

interface StudentAdmitFormProps {
    onSuccess?: () => void;
    onCancel?: () => void;
}

export function StudentAdmitForm({ onSuccess, onCancel }: StudentAdmitFormProps) {
    const [step, setStep] = useState(1);
    const [courses, setCourses] = useState<Course[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [phoneError, setPhoneError] = useState('');
    const [createdStudentId, setCreatedStudentId] = useState<string | null>(null);
    const [createdAdmissionId, setCreatedAdmissionId] = useState<string | null>(null);
    const [images, setImages] = useState<File[]>([]);
    const [previewImage, setPreviewImage] = useState<File | null>(null);
    const [showWebcam, setShowWebcam] = useState(false);
    const [uploadProgress, setUploadProgress] = useState<string | null>(null);
    const [trainingStatus, setTrainingStatus] = useState<'idle' | 'training' | 'success' | 'error'>('idle');
    const [trainingResult, setTrainingResult] = useState<{ faces_detected?: number; message?: string } | null>(null);
    const [dobDate, setDobDate] = useState<Date | null>(null);
    const [dobInputValue, setDobInputValue] = useState('');
    const fileInputRef = useRef<HTMLInputElement>(null);
    const folderInputRef = useRef<HTMLInputElement>(null);
    const isSubmittingRef = useRef(false);  // Idempotency: prevent double-submit
    
    const [formData, setFormData] = useState({
        first_name: '',
        last_name: '',
        course_id: '',
        date_of_birth: '',
        guardian_name: '',
        guardian_phone: '',
        address: '',
    });

    useEffect(() => {
        loadCourses();
    }, []);

    const loadCourses = async () => {
        try {
            const data = await getCourses();
            setCourses(data.courses);
        } catch (err) {
            setError('Failed to load courses');
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
        const { name, value } = e.target;
        
        // Prevent numeric and special char input for name fields
        if (['first_name', 'last_name', 'guardian_name'].includes(name) && /[^a-zA-Z\s]/.test(value)) {
            return;
        }

        // Validate guardian phone (only numbers, max 10 digits)
        if (name === 'guardian_phone') {
            if (!/^\d*$/.test(value)) return; // Only allow numbers
            if (value.length > 10) return;    // Max 10 digits
            
            // Check uniqueness if 10 digits
            if (value.length === 10) {
                checkGuardianPhone(value)
                    .then((res: { exists: boolean }) => {
                        if (res.exists) {
                            setPhoneError('Phone number already exists');
                        } else {
                            setPhoneError('');
                        }
                    })
                    .catch(() => {
                        // Ignore network errors for now, or ensure we don't block
                        // But if backend fails, maybe we shouldn't show "exists" error.
                        // We'll reset error if check fails/passes.
                        // Actually if length changed from 10 to something else, we should clear error.
                    });
            } else {
                setPhoneError('');
            }
        }

        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    const handleSubmitBasicInfo = async (e: FormEvent) => {
        e.preventDefault();
        
        // Idempotency: Block re-entry if already submitting
        if (isSubmittingRef.current) return;
        isSubmittingRef.current = true;
        
        setError('');
        
        // Frontend validation: Ensure course is selected
        if (!formData.course_id) {
            setError('Please select a course');
            return;
        }
        
        // Validate course_id is from the loaded courses list
        const isValidCourse = courses.some(c => c.course_id === formData.course_id);
        if (!isValidCourse) {
            setError('Invalid course selected. Please select a valid course from the list.');
            return;
        }
        
        // Validate phone number length (10 digits)
        if (formData.guardian_phone.length !== 10) {
            setError('Guardian Phone must be exactly 10 digits');
            return;
        }

        if (phoneError) {
            setError('Please correct the errors before saving.');
            return;
        }
        
        setLoading(true);

        try {
            const submitData = {
                ...formData,
                date_of_birth: dobDate ? format(dobDate, 'yyyy-MM-dd') : '',
            };
            const result = await admitStudent(submitData);
            setCreatedStudentId(result.student_id);
            setCreatedAdmissionId(result.admission_id);
            setStep(2);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to admit student');
        } finally {
            setLoading(false);
            isSubmittingRef.current = false;
        }
    };

    // Handle single/multiple file selection
    const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = Array.from(e.target.files || []);
        addImages(files);
        // Reset input so same files can be selected again
        e.target.value = '';
    };

    // Handle folder selection (webkitdirectory)
    const handleFolderSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = Array.from(e.target.files || []);
        // Filter only image files from folder
        const imageFiles = files.filter(file => 
            file.type.startsWith('image/') || 
            /\.(jpg|jpeg|png|gif|webp|bmp)$/i.test(file.name)
        );
        addImages(imageFiles);
        e.target.value = '';
    };

    // Allowed image extensions and MIME types
    const ALLOWED_EXTENSIONS = /\.(jpg|jpeg|png|webp|bmp|gif)$/i;
    const ALLOWED_MIME_PREFIXES = 'image/';

    // Add images with duplicate check, type validation, and limit
    const addImages = (newFiles: File[]) => {
        const validFiles: File[] = [];
        const rejected: string[] = [];
        
        for (const f of newFiles) {
            if (f.type.startsWith(ALLOWED_MIME_PREFIXES) || ALLOWED_EXTENSIONS.test(f.name)) {
                validFiles.push(f);
            } else {
                rejected.push(f.name);
            }
        }
        
        if (rejected.length > 0) {
            setError(`Rejected ${rejected.length} non-image file(s): ${rejected.slice(0, 3).join(', ')}${rejected.length > 3 ? '...' : ''}. Only JPG, PNG, WebP, BMP, GIF allowed.`);
        }
        
        setImages((prev) => {
            const existingNames = new Set(prev.map(f => f.name));
            const uniqueNew = validFiles.filter(f => !existingNames.has(f.name));
            const combined = [...prev, ...uniqueNew];
            return combined.slice(0, 250); // Max 250 images
        });
    };

    // Handle webcam capture
    const handleWebcamCapture = (file: File) => {
        addImages([file]);
    };

    const handleRemoveImage = (index: number) => {
        setImages((prev) => prev.filter((_, i) => i !== index));
    };

    const handleClearAllImages = () => {
        setImages([]);
    };

    const handleUploadImages = async () => {
        if (!createdAdmissionId || images.length === 0) return;
        
        setLoading(true);
        setError('');
        setUploadProgress('Uploading images...');
        
        try {
            // Step 1: Upload images
            await uploadStudentImages(createdAdmissionId, images);
            setUploadProgress('Images uploaded! Starting face training...');
            setStep(3); // Move to training step
            
            // Step 2: Auto-trigger training
            setTrainingStatus('training');
            try {
                const result = await trainStudentFace(createdAdmissionId);
                if (result.is_trained) {
                    setTrainingStatus('success');
                    setTrainingResult({ faces_detected: result.faces_detected, message: result.message });
                } else {
                    setTrainingStatus('error');
                    setTrainingResult({ message: result.message || 'Training failed' });
                }
            } catch (trainErr: any) {
                setTrainingStatus('error');
                setTrainingResult({ message: trainErr.response?.data?.detail || 'Training failed' });
            }
            
            setUploadProgress(null);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to upload images');
            setUploadProgress(null);
        } finally {
            setLoading(false);
        }
    };

    const handleComplete = () => {
        onSuccess?.();
    };

    return (
        <div className={styles.container}>
            <div className={styles.steps}>
                <div className={`${styles.step} ${step >= 1 ? styles.active : ''}`}>
                    <span>1</span> Basic Info
                </div>
                <div className={styles.stepLine} />
                <div className={`${styles.step} ${step >= 2 ? styles.active : ''}`}>
                    <span>2</span> Face Images
                </div>
                <div className={styles.stepLine} />
                <div className={`${styles.step} ${step >= 3 ? styles.active : ''}`}>
                    <span>3</span> Complete
                </div>
            </div>

            {error && <div className={styles.error}>{error}</div>}

            {step === 1 && (
                <form onSubmit={handleSubmitBasicInfo} className={styles.form}>
                    <div className={styles.row}>
                        <div className={styles.field}>
                            <label>First Name *</label>
                            <input type="text" name="first_name" value={formData.first_name} onChange={handleChange} required />
                        </div>
                        <div className={styles.field}>
                            <label>Last Name *</label>
                            <input type="text" name="last_name" value={formData.last_name} onChange={handleChange} required />
                        </div>
                    </div>

                    <div className={styles.row}>
                        <div className={styles.field}>
                            <label>Course *</label>
                            <select name="course_id" value={formData.course_id} onChange={handleChange} required>
                                <option value="">Select Course</option>
                                {courses.map((c) => (
                                    <option key={c.course_id} value={c.course_id}>{c.name} - {c.section}</option>
                                ))}
                            </select>
                        </div>
                        <div className={styles.field}>
                            <label>Date of Birth *</label>
                            <DatePicker
                                selected={dobDate}
                                onChange={(date: Date | null) => {
                                    setDobDate(date);
                                    if (date) {
                                        setDobInputValue(format(date, 'dd-MM-yyyy'));
                                    } else {
                                        setDobInputValue('');
                                    }
                                }}
                                onChangeRaw={(e) => {
                                    if (!e || !e.target) return;
                                    const val = (e.target as HTMLInputElement).value;
                                    // Only mask if user is typing (not calendar selection)
                                    if (e.type === 'change') {
                                        e.preventDefault();
                                        const masked = maskDateInput(val);
                                        setDobInputValue(masked);
                                        if (masked.length === 10) {
                                            const [d, m, y] = masked.split('-').map(Number);
                                            const date = new Date(y, m - 1, d);
                                            if (!isNaN(date.getTime()) && date.getFullYear() === y) {
                                                setDobDate(date);
                                            }
                                        }
                                    }
                                }}
                                value={dobInputValue}
                                dateFormat="dd-MM-yyyy"
                                placeholderText="DD-MM-YYYY"
                                className={styles.datePicker}
                                isClearable
                                showMonthDropdown
                                showYearDropdown
                                dropdownMode="select"
                                maxDate={new Date()}
                                yearDropdownItemNumber={100}
                                scrollableYearDropdown
                                portalId="root"
                                required
                                autoComplete="off"
                                shouldCloseOnSelect={true}
                            />
                        </div>
                    </div>

                    <div className={styles.row}>
                        <div className={styles.field}>
                            <label>Guardian Name *</label>
                            <input type="text" name="guardian_name" value={formData.guardian_name} onChange={handleChange} required />
                        </div>
                        <div className={styles.field}>
                            <label>Guardian Phone *</label>
                            <input 
                                type="tel" 
                                name="guardian_phone" 
                                value={formData.guardian_phone} 
                                onChange={handleChange} 
                                required 
                                minLength={10} 
                                maxLength={10} 
                                pattern="[0-9]{10}"
                                title="10 digit mobile number"
                                className={phoneError ? styles.inputError : ''}
                            />
                            {phoneError && <span className={styles.errorMessage}>{phoneError}</span>}
                        </div>
                    </div>

                    <div className={styles.field}>
                        <label>Address</label>
                        <textarea name="address" value={formData.address} onChange={handleChange} rows={2} placeholder="Optional" />
                    </div>

                    <div className={styles.actions}>
                        {onCancel && <button type="button" onClick={onCancel} className={styles.cancelBtn}>Cancel</button>}
                        <button type="submit" disabled={loading} className={styles.submitBtn}>
                            {loading ? 'Saving...' : 'Next: Add Photos'}
                        </button>
                    </div>
                </form>
            )}

            {step === 2 && (
                <div className={styles.imageStep}>
                    <h3>Upload Face Images</h3>
                    <p>Upload 5-250 clear face images for recognition training. You can use webcam, select files, or upload an entire folder.</p>
                    
                    {/* Image source buttons */}
                    <div className={styles.imageSourceBtns}>
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

                    {/* Hidden file inputs */}
                    <input
                        ref={fileInputRef}
                        type="file"
                        accept="image/jpeg,image/png,image/webp,image/bmp,image/gif"
                        multiple
                        onChange={handleImageSelect}
                        style={{ display: 'none' }}
                    />
                    <input
                        ref={folderInputRef}
                        type="file"
                        accept="image/jpeg,image/png,image/webp,image/bmp,image/gif"
                        // @ts-ignore - webkitdirectory is a valid attribute
                        webkitdirectory=""
                        // @ts-ignore
                        directory=""
                        multiple
                        onChange={handleFolderSelect}
                        style={{ display: 'none' }}
                    />

                    {/* Image preview grid */}
                    {images.length > 0 && (
                        <>
                            <div className={styles.imageHeader}>
                                <span className={styles.imageCount}>{images.length} / 250 images selected</span>
                                <button 
                                    type="button" 
                                    onClick={handleClearAllImages} 
                                    className={styles.clearBtn}
                                >
                                    Clear All
                                </button>
                            </div>
                            <div className={styles.imageGrid}>
                                {images.map((img, i) => (
                                    <div 
                                        key={`${img.name}-${i}`} 
                                        className={styles.imagePreview}
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
                                        <span className={styles.imageName}>{img.name.length > 12 ? img.name.slice(0, 10) + '...' : img.name}</span>
                                    </div>
                                ))}
                            </div>
                        </>
                    )}

                    {images.length === 0 && (
                        <div className={styles.emptyState}>
                            <span className={styles.emptyIcon}>📸</span>
                            <p>No images added yet. Use the buttons above to add face images.</p>
                        </div>
                    )}

                    {uploadProgress && (
                        <div className={styles.progressBar}>
                            <div className={styles.progressText}>{uploadProgress}</div>
                        </div>
                    )}

                    <div className={styles.actions}>
                        <button onClick={() => setStep(3)} className={styles.skipBtn}>Skip for Now</button>
                        <button 
                            onClick={handleUploadImages} 
                            disabled={loading || images.length < 5} 
                            className={styles.submitBtn}
                            title={images.length > 0 && images.length < 5 ? "Minimum 5 images required" : "Upload and start training"}
                        >
                            {loading ? 'Uploading...' : `Upload ${images.length} Image${images.length !== 1 ? 's' : ''}`}
                        </button>
                        {images.length > 0 && images.length < 5 && (
                            <div className={styles.warningText}>⚠ Please upload at least 5 images</div>
                        )}
                    </div>
                </div>
            )}

            {step === 3 && (
                <div className={styles.trainingStep}>
                    {trainingStatus === 'training' && (
                        <>
                            <h3>🎓 Face Recognition Training</h3>
                            <p>Student ID: <code>{createdStudentId}</code></p>
                            <div className={styles.trainingProgress}>
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
                                <p className={styles.trainingText}>
                                    <span className={styles.trainingPhase}>Analyzing facial features...</span>
                                </p>
                                <div className={styles.progressSteps}>
                                    <span className={styles.progressDot}></span>
                                    <span className={styles.progressDot}></span>
                                    <span className={styles.progressDot}></span>
                                </div>
                                <p className={styles.note}>This may take a few moments depending on the number of images.</p>
                            </div>
                        </>
                    )}
                    
                    {trainingStatus === 'success' && (
                        <div className={styles.completeContent}>
                            <div className={styles.successIcon}>✓</div>
                            <h3>Student Admitted Successfully!</h3>
                            <p>Student ID: <code>{createdStudentId}</code></p>
                            <p>The student can now log in with their credentials.</p>
                            <p className={styles.note}>
                                ✓ Face recognition is trained and ready for attendance.
                                {trainingResult?.faces_detected && ` (${trainingResult.faces_detected} face(s) processed)`}
                            </p>
                            <button onClick={handleComplete} className={styles.submitBtn}>Done</button>
                        </div>
                    )}
                    
                    {trainingStatus === 'error' && (
                        <div className={styles.completeContent}>
                            <div className={styles.successIcon}>✓</div>
                            <h3>Student Admitted Successfully!</h3>
                            <p>Student ID: <code>{createdStudentId}</code></p>
                            <p>The student can now log in with their credentials.</p>
                            <p className={styles.noteWarning}>
                                ⚠ Face training failed: {trainingResult?.message || 'Unknown error'}. You can retry from student list.
                            </p>
                            <button onClick={handleComplete} className={styles.submitBtn}>Done</button>
                        </div>
                    )}
                    
                    {trainingStatus === 'idle' && (
                        <div className={styles.completeContent}>
                            <div className={styles.successIcon}>✓</div>
                            <h3>Student Admitted Successfully!</h3>
                            <p>Student ID: <code>{createdStudentId}</code></p>
                            <p>The student can now log in with their credentials.</p>
                            <p className={styles.noteWarning}>
                                ⚠ Face images not uploaded. You can add them later from student list.
                            </p>
                            <button onClick={handleComplete} className={styles.submitBtn}>Done</button>
                        </div>
                    )}
                </div>
            )}

            {/* Webcam capture modal */}
            {showWebcam && (
                <WebcamCapture
                    onCapture={handleWebcamCapture}
                    onClose={() => setShowWebcam(false)}
                    maxCaptures={250}
                    capturedCount={images.length}
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
