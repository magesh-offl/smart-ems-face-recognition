"""AdaFace Recognition Model

Quality-adaptive margin for face recognition.
Reference: https://github.com/mk-minchul/AdaFace
"""
import os
import numpy as np
import torch
import torch.nn as nn
from typing import Optional, Tuple
from torchvision import transforms

# Default paths
WEIGHTS_DIR = os.path.join(os.path.dirname(__file__), "weights")


class AdaFaceRecognizer:
    """AdaFace face recognition model wrapper"""
    
    def __init__(
        self, 
        model_path: Optional[str] = None,
        device: Optional[torch.device] = None
    ):
        """
        Initialize AdaFace recognizer.
        
        Args:
            model_path: Path to pre-trained weights
            device: Torch device (auto-detect if None)
        """
        self.model_path = model_path
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._model = None
        
        # Preprocessing transform
        # IMPORTANT: AdaFace uses BGR input (same as cv2), not RGB!
        self.transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Resize((112, 112)),
            transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
        ])
    
    def _load_model(self):
        """Lazy load the model"""
        if self._model is None:
            # Prioritize original AdaFace ckpt from GitHub
            original_ckpt = os.path.join(WEIGHTS_DIR, "adaface_ir100_webface12m.ckpt")
            alt_ckpt = os.path.join(WEIGHTS_DIR, "adaface_ir101_webface12m.ckpt")
            
            if os.path.exists(original_ckpt):
                self.model_path = original_ckpt
            elif os.path.exists(alt_ckpt):
                self.model_path = alt_ckpt
            else:
                raise FileNotFoundError(
                    f"AdaFace model not found.\n"
                    f"Checked: {original_ckpt}\n"
                    f"Checked: {alt_ckpt}\n"
                    "Please download from: https://github.com/mk-minchul/AdaFace"
                )
            
            # Load AdaFace model with native backbone
            from .net import build_model
            
            self._model = build_model("ir_101")
            
            # Load weights
            checkpoint = torch.load(self.model_path, map_location=self.device, weights_only=False)
            if 'state_dict' in checkpoint:
                state_dict = checkpoint['state_dict']
            else:
                state_dict = checkpoint
            
            # Filter out head weights and remove 'model.' prefix
            new_state_dict = {}
            for k, v in state_dict.items():
                # Skip head weights (classification head, not needed for embeddings)
                if k.startswith('head.'):
                    continue
                
                # Remove 'model.' prefix if present
                new_key = k
                if k.startswith('model.'):
                    new_key = k[6:]  # Remove 'model.'
                
                new_state_dict[new_key] = v
            
            # Load weights into model
            missing, unexpected = self._model.load_state_dict(new_state_dict, strict=False)
            
            if missing:
                import logging
                logging.getLogger(__name__).info(f"AdaFace loaded with {len(missing)} missing keys (expected for head)")
            
            self._model.to(self.device)
            self._model.eval()
            
        return self._model
    
    def get_embedding(self, face_image: np.ndarray) -> np.ndarray:
        """
        Extract face embedding from aligned face image.
        
        Args:
            face_image: Aligned face image (BGR, 112x112)
            
        Returns:
            512-dimensional embedding vector
        """
        import cv2
        
        model = self._load_model()
        
        # AdaFace expects BGR input (same as cv2 default)
        # No color conversion needed if input is BGR
        
        # Preprocess
        face_tensor = self.transform(face_image).unsqueeze(0).to(self.device)
        
        # Get embedding - AdaFace returns (output, norm) tuple
        with torch.no_grad():
            output, norm = model(face_tensor)
            embedding = output.cpu().numpy()[0]
        
        # Already normalized by the model
        return embedding
    
    def __call__(self, face_tensor: torch.Tensor) -> torch.Tensor:
        """
        Forward pass for batch processing.
        Compatible with ArcFace interface - returns just the embeddings.
        """
        model = self._load_model()
        with torch.no_grad():
            output, norm = model(face_tensor)
            return output
