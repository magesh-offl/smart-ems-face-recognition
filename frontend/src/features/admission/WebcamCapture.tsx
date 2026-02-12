import { useState, useRef, useEffect, useCallback } from 'react';
import styles from './WebcamCapture.module.css';

interface WebcamCaptureProps {
    onCapture: (imageFile: File) => void;
    onClose: () => void;
    maxCaptures?: number;
    capturedCount?: number;
}

export function WebcamCapture({ onCapture, onClose, maxCaptures = 10, capturedCount = 0 }: WebcamCaptureProps) {
    const videoRef = useRef<HTMLVideoElement>(null);
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [stream, setStream] = useState<MediaStream | null>(null);
    const streamRef = useRef<MediaStream | null>(null);
    const [error, setError] = useState('');
    const [countdown, setCountdown] = useState<number | null>(null);
    const [isCameraReady, setIsCameraReady] = useState(false);
    const [facingMode, setFacingMode] = useState<'user' | 'environment'>('user');
    const [isAutoCapturing, setIsAutoCapturing] = useState(false);
    const autoCaptureRef = useRef<ReturnType<typeof setInterval> | null>(null);
    const capturedCountRef = useRef(capturedCount);
    const onCaptureRef = useRef(onCapture);

    // Keep refs in sync with latest props
    useEffect(() => {
        capturedCountRef.current = capturedCount;
    }, [capturedCount]);

    useEffect(() => {
        onCaptureRef.current = onCapture;
    }, [onCapture]);

    // Start webcam
    const startCamera = useCallback(async () => {
        try {
            setError('');
            const mediaStream = await navigator.mediaDevices.getUserMedia({
                video: {
                    facingMode,
                    width: { ideal: 640 },
                    height: { ideal: 480 }
                },
                audio: false
            });
            
            if (videoRef.current) {
                videoRef.current.srcObject = mediaStream;
                streamRef.current = mediaStream;
                setStream(mediaStream);
            }
        } catch (err) {
            console.error('Camera error:', err);
            setError('Unable to access camera. Please ensure camera permissions are granted.');
        }
    }, [facingMode]);

    useEffect(() => {
        startCamera();
        
        return () => {
            // Use ref to always get the latest stream for cleanup
            if (streamRef.current) {
                streamRef.current.getTracks().forEach(track => track.stop());
                streamRef.current = null;
            }
        };
    }, [startCamera]);

    // Cleanup auto-capture on unmount
    useEffect(() => {
        return () => {
            if (autoCaptureRef.current) {
                clearInterval(autoCaptureRef.current);
            }
        };
    }, []);

    const handleVideoReady = () => {
        setIsCameraReady(true);
    };

    const switchCamera = async () => {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }
        setFacingMode(prev => prev === 'user' ? 'environment' : 'user');
    };

    // Capture a single frame — uses ref so it always calls latest onCapture
    const capturePhoto = useCallback(() => {
        if (!videoRef.current || !canvasRef.current) return;

        const video = videoRef.current;
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        
        if (!ctx) return;

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        ctx.drawImage(video, 0, 0);

        canvas.toBlob((blob) => {
            if (blob) {
                const timestamp = Date.now();
                const file = new File([blob], `webcam_capture_${timestamp}.jpg`, { type: 'image/jpeg' });
                onCaptureRef.current(file);
            }
        }, 'image/jpeg', 0.92);
    }, []); // No dependencies — uses refs internally

    // Start auto-capture: countdown 3-2-1 then continuously capture
    const startAutoCapture = () => {
        setCountdown(3);
    };

    // Stop auto-capture
    const stopAutoCapture = useCallback(() => {
        if (autoCaptureRef.current) {
            clearInterval(autoCaptureRef.current);
            autoCaptureRef.current = null;
        }
        setIsAutoCapturing(false);
    }, []);

    // Countdown → then begin interval-based auto-capture
    useEffect(() => {
        if (countdown === null) return;

        if (countdown > 0) {
            const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
            return () => clearTimeout(timer);
        } else {
            // Countdown finished → start auto-capturing
            setCountdown(null);
            setIsAutoCapturing(true);

            // Capture immediately once
            capturePhoto();

            // Then capture every 1 second
            autoCaptureRef.current = setInterval(() => {
                if (capturedCountRef.current >= maxCaptures) {
                    stopAutoCapture();
                    return;
                }
                capturePhoto();
            }, 1000);
        }
    }, [countdown, capturePhoto, maxCaptures, stopAutoCapture]);

    // Stop when limit is reached
    useEffect(() => {
        if (isAutoCapturing && capturedCount >= maxCaptures) {
            stopAutoCapture();
        }
    }, [capturedCount, maxCaptures, isAutoCapturing, stopAutoCapture]);

    const captureInstant = () => {
        capturePhoto();
    };

    const remaining = maxCaptures - capturedCount;

    return (
        <div className={styles.overlay}>
            <div className={styles.modal}>
                <div className={styles.header}>
                    <h3>📸 Capture Face Images</h3>
                    <button onClick={() => { stopAutoCapture(); onClose(); }} className={styles.closeBtn}>×</button>
                </div>

                <div className={styles.videoContainer}>
                    {error ? (
                        <div className={styles.errorOverlay}>
                            <span>⚠️</span>
                            <p>{error}</p>
                            <button onClick={startCamera}>Retry</button>
                        </div>
                    ) : (
                        <>
                            <video
                                ref={videoRef}
                                autoPlay
                                playsInline
                                muted
                                onLoadedMetadata={handleVideoReady}
                                className={styles.video}
                            />
                            {countdown !== null && (
                                <div className={styles.countdown}>{countdown}</div>
                            )}
                            {isAutoCapturing && (
                                <div className={styles.autoCaptureBadge}>
                                    ● Auto-capturing...
                                </div>
                            )}
                            {!isCameraReady && (
                                <div className={styles.loading}>Starting camera...</div>
                            )}
                        </>
                    )}
                </div>

                <canvas ref={canvasRef} style={{ display: 'none' }} />

                <div className={styles.info}>
                    <span className={styles.counter}>{capturedCount} / {maxCaptures} images captured</span>
                    {remaining <= 3 && remaining > 0 && (
                        <span className={styles.warning}>({remaining} remaining)</span>
                    )}
                </div>

                <div className={styles.controls}>
                    <button 
                        onClick={switchCamera} 
                        className={styles.secondaryBtn}
                        title="Switch Camera"
                        disabled={isAutoCapturing}
                    >
                        🔄 Switch
                    </button>
                    {!isAutoCapturing ? (
                        <button 
                            onClick={startAutoCapture} 
                            className={styles.captureBtn}
                            disabled={!isCameraReady || countdown !== null || remaining <= 0}
                        >
                            {countdown !== null ? countdown : '🎥'} Auto Capture
                        </button>
                    ) : (
                        <button 
                            onClick={stopAutoCapture} 
                            className={styles.stopBtn}
                        >
                            ⏹ Stop
                        </button>
                    )}
                    <button 
                        onClick={captureInstant} 
                        className={styles.captureBtn}
                        disabled={!isCameraReady || remaining <= 0 || isAutoCapturing}
                    >
                        📷 Capture
                    </button>
                </div>

                <div className={styles.tips}>
                    <strong>Tips:</strong> Look directly at camera • Ensure good lighting • Move head slowly for different angles during auto-capture
                </div>

                <div className={styles.footer}>
                    <button onClick={() => { stopAutoCapture(); onClose(); }} className={styles.doneBtn}>
                        Done ({capturedCount} images)
                    </button>
                </div>
            </div>
        </div>
    );
}
