"""ID Counter Document Model for Atomic ID Generation"""
from datetime import datetime
from typing import Dict, Any
from .base import BaseDocument


class IDCounterDocument(BaseDocument):
    """MongoDB document model for ID counters.
    
    Used for atomic sequential ID generation.
    Each counter tracks a specific entity type with optional scope.
    
    Examples:
        - {"counter_type": "user_2602", "prefix": "USR2602", "current_value": 5}
        - {"counter_type": "student_26_003", "prefix": "STU26003", "current_value": 12}
    """
    
    collection_name = "id_counters"
    
    @staticmethod
    def create(
        counter_type: str,
        prefix: str,
        current_value: int = 0
    ) -> Dict[str, Any]:
        """Create a new ID counter document.
        
        Args:
            counter_type: Unique identifier for counter scope 
                         (e.g., "user_2602", "student_26_003")
            prefix: The prefix part of generated IDs (e.g., "USR2602", "STU26003")
            current_value: Starting counter value (default 0)
            
        Returns:
            Document dictionary ready for MongoDB insertion
        """
        doc = {
            "counter_type": counter_type,
            "prefix": prefix,
            "current_value": current_value,
            **BaseDocument.get_base_fields()
        }
        return doc
