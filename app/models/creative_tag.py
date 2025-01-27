from dataclasses import dataclass
from typing import List, Optional, Dict

@dataclass
class ProcessingResult:
    ucrid: str
    status: str
    tags: Optional[List[Dict]] = None
    error: Optional[str] = None
    processing_time: float = 0.0

@dataclass
class Creative:
    ucrid: str
    media_url: str 