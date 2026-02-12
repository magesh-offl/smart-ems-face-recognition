
import { useEffect } from 'react';
import styles from './ImagePreviewOverlay.module.css';

interface ImagePreviewOverlayProps {
    image: File | null;
    onClose: () => void;
}

export function ImagePreviewOverlay({ image, onClose }: ImagePreviewOverlayProps) {
    useEffect(() => {
        const handleEsc = (e: KeyboardEvent) => {
            if (e.key === 'Escape') onClose();
        };
        window.addEventListener('keydown', handleEsc);
        return () => window.removeEventListener('keydown', handleEsc);
    }, [onClose]);

    if (!image) return null;

    const imageUrl = URL.createObjectURL(image);

    return (
        <div className={styles.overlay} onClick={onClose}>
            <div className={styles.content} onClick={e => e.stopPropagation()}>
                <button className={styles.closeBtn} onClick={onClose}>×</button>
                <img src={imageUrl} alt={image.name} className={styles.image} />
                <div className={styles.caption}>{image.name}</div>
            </div>
        </div>
    );
}
