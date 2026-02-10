"""Agentic diary generation system"""
import json
from typing import List, Dict, Any, Optional, Union
from datetime import date
from concurrent.futures import ThreadPoolExecutor, as_completed
from pydantic import BaseModel, Field

from .llm_client import get_llm_client
from .vtu_skills import get_skills_list, format_skills_for_prompt
from src.date_management import DateManager
from config import (
    BATCH_SIZE_DAYS,
    DEFAULT_HOURS_PER_DAY,
    MIN_ENTRY_WORDS,
    MAX_ENTRY_WORDS,
    CONFIDENCE_THRESHOLD,
    SYSTEM_PROMPTS_DIR
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DiaryEntry(BaseModel):
    """Single diary entry"""
    date: str = Field(description="Date in YYYY-MM-DD format")
    hours: float = Field(description="Hours worked (1-8)", ge=1.0, le=8.0)
    activities: str = Field(description="Detailed description (120-180 words)")
    learnings: str = Field(description="Learning summary")
    blockers: str = Field(description="Blockers or challenges", default="None")
    links: str = Field(description="Related links", default="")
    skills: List[str] = Field(description="VTU skill names", min_items=1, max_items=5)
    confidence: float = Field(description="Confidence score 0-1", ge=0.0, le=1.0)


class MultiDayOutput(BaseModel):
    """Output for multiple diary entries"""
    entries: List[DiaryEntry]
    warnings: List[str] = Field(default_factory=list)
    total_generated: int = 0


class DiaryGenerationAgent:
    """
    Agentic system for generating diary entries.

    Uses LLM with tools for:
    - Skill matching
    - Content expansion
    - Multi-day batch generation
    """

    def __init__(self, llm_client=None):
        self.llm = llm_client or get_llm_client()
        self.date_manager = DateManager()
        self.skills_list = get_skills_list()

        # Load system prompts
        self.system_prompt = self._load_prompt("multi_day_system.txt")

        logger.info("Diary Generation Agent initialized")

    def _load_prompt(self, filename: str) -> str:
        """Load system prompt from file"""
        prompt_path = SYSTEM_PROMPTS_DIR / filename
        if prompt_path.exists():
            return prompt_path.read_text()
        else:
            logger.warning(f"Prompt file not found: {filename}, using fallback")
            return self._get_fallback_prompt()

    def _get_fallback_prompt(self) -> str:
        """Fallback system prompt"""
        return """You are an expert internship diary entry generator for VTU's Internyet portal.

Generate detailed, professional diary entries for multiple dates based on provided input data.

OUTPUT FORMAT: Return a JSON array of diary entries with this structure:
[
  {
    "date": "YYYY-MM-DD",
    "hours": 7.0,
    "activities": "<120-180 word detailed description>",
    "learnings": "<1-2 sentences on technical skills gained>",
    "blockers": "Description of challenges or 'None'",
    "links": "",
    "skills": ["Skill 1", "Skill 2", "Skill 3"],
    "confidence": 0.95
  }
]

RULES:
1. Activities MUST be 120-180 words
2. Vary wording across days to avoid repetition
3. Use realistic, professional language
4. Include learning curves, debugging challenges
5. Skills must be from provided VTU skill list
6. Confidence: 0.9+ for detailed input, 0.7-0.9 for general, <0.7 for sparse
"""

    def generate_single(
        self,
        raw_text: str,
        target_date: Optional[date] = None,
        hours: Optional[float] = None
    ) -> DiaryEntry:
        """Generate single diary entry"""

        if target_date is None:
            target_date = date.today()

        # Build prompt with full skills list for LLM to choose from
        skills_formatted = format_skills_for_prompt()
        prompt = f"""
Generate a diary entry for {target_date.isoformat()}.

Input data: {raw_text}

Hours: {hours or DEFAULT_HOURS_PER_DAY}

IMPORTANT: Select 1-3 most relevant skills from this list based on the activities described:
{skills_formatted}

Return JSON matching the DiaryEntry schema with skills array containing EXACT names from the list above.
"""

        # Generate
        response = self.llm.generate(
            prompt=prompt,
            system=self.system_prompt,
            json_mode=True
        )

        # Parse and validate
        if isinstance(response, list) and len(response) > 0:
            entry_data = response[0]
        else:
            entry_data = response

        entry = DiaryEntry(**entry_data)
        return entry

    def generate_bulk(
        self,
        input_data: Union[str, List[Dict[str, Any]]],
        target_dates: List[date],
        distribute_content: bool = True
    ) -> MultiDayOutput:
        """
        Generate entries for multiple dates.

        Args:
            input_data: Raw text or list of per-day data chunks
            target_dates: List of dates to generate for
            distribute_content: If True and input is sparse, distribute across dates

        Returns:
            MultiDayOutput with all entries
        """
        logger.info(f"Generating bulk entries for {len(target_dates)} dates")

        # Check if we have per-day data or need to distribute
        if isinstance(input_data, str):
            # Single raw text - distribute across all dates
            return self._generate_distributed(input_data, target_dates)

        elif isinstance(input_data, list):
            # List of per-day data
            if len(input_data) == len(target_dates):
                # 1:1 mapping
                return self._generate_mapped(input_data, target_dates)
            else:
                # Distribute available data
                return self._generate_distributed(input_data, target_dates)

    def _generate_distributed(
        self,
        raw_text: str,
        target_dates: List[date]
    ) -> MultiDayOutput:
        """Distribute content across multiple dates"""

        # Batch dates for efficient API calls
        batches = [
            target_dates[i:i + BATCH_SIZE_DAYS]
            for i in range(0, len(target_dates), BATCH_SIZE_DAYS)
        ]

        all_entries = []
        warnings = []

        # Process batches in parallel
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            for batch in batches:
                future = executor.submit(
                    self._generate_batch,
                    raw_text,
                    batch
                )
                futures.append(future)

            for future in as_completed(futures):
                try:
                    result = future.result()
                    all_entries.extend(result["entries"])
                    warnings.extend(result.get("warnings", []))
                except Exception as e:
                    logger.error(f"Batch generation failed: {e}")
                    warnings.append(f"Batch failed: {str(e)}")

        return MultiDayOutput(
            entries=all_entries,
            warnings=warnings,
            total_generated=len(all_entries)
        )

    def _generate_batch(
        self,
        raw_text: str,
        dates: List[date]
    ) -> Dict[str, Any]:
        """Generate entries for a batch of dates"""

        date_strs = [d.isoformat() for d in dates]

        # Include full skills list for LLM to choose from
        skills_formatted = format_skills_for_prompt()

        prompt = f"""
Generate diary entries for the following dates: {', '.join(date_strs)}

Input data: {raw_text}

SELECT RELEVANT SKILLS FROM THIS LIST (choose 1-3 per entry):
{skills_formatted}

IMPORTANT:
- Generate {len(dates)} distinct entries
- Vary wording and focus for each day
- Distribute work phases across dates (setup → development → testing → docs)
- Each entry 120-180 words
- Use EXACT skill names from the list above
- Return as JSON array

Return ONLY valid JSON array matching the schema.
"""

        try:
            response = self.llm.generate(
                prompt=prompt,
                system=self.system_prompt,
                json_mode=True,
                max_tokens=4000
            )

            # Handle response
            if isinstance(response, dict) and "entries" in response:
                entries_data = response["entries"]
            elif isinstance(response, list):
                entries_data = response
            else:
                raise ValueError(f"Unexpected response format: {type(response)}")

            # Parse entries
            entries = []
            for entry_data in entries_data:
                try:
                    entry = DiaryEntry(**entry_data)
                    entries.append(entry)
                except Exception as e:
                    logger.warning(f"Failed to parse entry: {e}")
                    continue

            return {"entries": entries, "warnings": []}

        except Exception as e:
            logger.error(f"Batch generation failed: {e}")
            return {"entries": [], "warnings": [str(e)]}

    def _generate_mapped(
        self,
        data_chunks: List[Dict[str, Any]],
        target_dates: List[date]
    ) -> MultiDayOutput:
        """Generate entries with 1:1 data-to-date mapping"""

        all_entries = []
        warnings = []

        for data, target_date in zip(data_chunks, target_dates):
            try:
                raw_text = data.get("raw_text", "")
                hours = data.get("metadata", {}).get("hours")

                entry = self.generate_single(
                    raw_text=raw_text,
                    target_date=target_date,
                    hours=hours
                )

                all_entries.append(entry)

            except Exception as e:
                logger.error(f"Failed to generate entry for {target_date}: {e}")
                warnings.append(f"{target_date}: {str(e)}")

        return MultiDayOutput(
            entries=all_entries,
            warnings=warnings,
            total_generated=len(all_entries)
        )

    def filter_by_confidence(
        self,
        output: MultiDayOutput,
        threshold: float = CONFIDENCE_THRESHOLD
    ) -> Dict[str, List[DiaryEntry]]:
        """Filter entries by confidence threshold"""

        high_confidence = []
        needs_review = []

        for entry in output.entries:
            if entry.confidence >= threshold:
                high_confidence.append(entry)
            else:
                needs_review.append(entry)

        logger.info(
            f"Confidence filter: {len(high_confidence)} high, "
            f"{len(needs_review)} need review"
        )

        return {
            "auto_submit": high_confidence,
            "manual_review": needs_review
        }
