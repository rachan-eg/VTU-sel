from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, field_validator
import json

class Activity(BaseModel):
    start: Optional[str] = None
    end: Optional[str] = None
    duration_minutes: Optional[int] = None
    short_description: str
    artifacts: List[str] = []
    tags: List[str] = []
    inferred: bool = False

class DiaryEntry(BaseModel):
    date: str
    entry_text: str = Field(..., description="120-180 words")
    activities: List[Activity]
    declaration: str
    confidence_score: int
    uncertainties: List[str] = []

    @field_validator("entry_text")
    @classmethod
    def validate_word_count(cls, v):
        word_count = len(v.split())
        if word_count < 120 or word_count > 180:
            pass
        return v

def validate_and_format(data: Dict[str, Any]) -> DiaryEntry:
    return DiaryEntry(**data)

def check_word_count(text: str) -> Dict[str, Any]:
    count = len(text.split())
    return {
        "count": count,
        "valid": 120 <= count <= 180,
        "status": "OK" if 120 <= count <= 180 else ("TOO_SHORT" if count < 120 else "TOO_LONG")
    }
