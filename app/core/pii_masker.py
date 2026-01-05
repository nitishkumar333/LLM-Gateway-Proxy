from typing import Dict
import re

class PIIMasker:
    """Detects and masks PII in text"""
    
    PATTERNS = {
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
        "credit_card": r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
    }
    
    @classmethod
    def mask_text(cls, text: str) -> tuple[str, Dict[str, int]]:
        """Mask PII and return masked text + detection counts"""
        masked = text
        detections = {}
        
        for pii_type, pattern in cls.PATTERNS.items():
            matches = re.finditer(pattern, masked)
            count = 0
            for match in matches:
                masked = masked.replace(match.group(), f"[REDACTED_{pii_type.upper()}]")
                count += 1
            if count > 0:
                detections[pii_type] = count
        
        return masked, detections
