"""Excel/CSV processor for bulk diary entries"""
from typing import List, Dict, Any
from pathlib import Path
import pandas as pd
from datetime import datetime

from src.utils.logger import get_logger

logger = get_logger(__name__)


class ExcelProcessor:
    """Processes Excel/CSV files with diary data"""

    # Column name variations to detect
    DATE_COLUMNS = ["date", "day", "when", "fecha", "datum"]
    HOURS_COLUMNS = ["hours", "duration", "time", "horas", "heures"]
    ACTIVITY_COLUMNS = ["activity", "activities", "work", "tasks", "keywords", "description", "notes"]
    SKILLS_COLUMNS = ["skills", "skill", "competencias", "compétences"]

    def process(self, file_path: str) -> List[Dict[str, Any]]:
        """Process Excel/CSV file into list of diary entries"""
        file_path = Path(file_path)
        logger.info(f"Processing Excel/CSV: {file_path.name}")

        # Read file
        if file_path.suffix.lower() == ".csv":
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        logger.info(f"Loaded {len(df)} rows, columns: {df.columns.tolist()}")

        # Auto-detect columns
        date_col = self._detect_column(df, self.DATE_COLUMNS)
        hours_col = self._detect_column(df, self.HOURS_COLUMNS)
        activity_col = self._detect_column(df, self.ACTIVITY_COLUMNS)
        skills_col = self._detect_column(df, self.SKILLS_COLUMNS)

        if not activity_col:
            raise ValueError(
                f"Could not find activity/work column. "
                f"Available columns: {df.columns.tolist()}"
            )

        logger.info(f"Detected columns - Date: {date_col}, Hours: {hours_col}, Activity: {activity_col}")

        # Process each row
        entries = []
        for idx, row in df.iterrows():
            try:
                entry = self._process_row(
                    row,
                    date_col=date_col,
                    hours_col=hours_col,
                    activity_col=activity_col,
                    skills_col=skills_col,
                    row_number=idx + 1
                )

                if entry:  # Skip empty rows
                    entries.append(entry)

            except Exception as e:
                logger.warning(f"Skipping row {idx + 1}: {e}")
                continue

        logger.info(f"Processed {len(entries)} valid entries from Excel")
        return entries

    def _detect_column(self, df: pd.DataFrame, keywords: List[str]) -> str:
        """Detect column by matching keywords"""
        for col in df.columns:
            col_lower = str(col).lower().strip()
            if any(kw in col_lower for kw in keywords):
                return col
        return None

    def _process_row(
        self,
        row: pd.Series,
        date_col: str,
        hours_col: str,
        activity_col: str,
        skills_col: str,
        row_number: int
    ) -> Dict[str, Any]:
        """Process single row into entry data"""

        # Extract activity text
        activity_text = str(row[activity_col]).strip() if activity_col else ""

        # Skip empty rows
        if not activity_text or activity_text.lower() in ["nan", "none", ""]:
            return None

        # Extract date
        date_value = None
        if date_col and pd.notna(row[date_col]):
            try:
                # Try parsing as date
                date_value = pd.to_datetime(row[date_col]).date().isoformat()
            except:
                # If it's a string, keep as is for later inference
                date_value = str(row[date_col]).strip()

        # Extract hours
        hours_value = None
        if hours_col and pd.notna(row[hours_col]):
            try:
                hours_value = float(row[hours_col])
            except:
                pass

        # Extract skills if present
        skills_value = None
        if skills_col and pd.notna(row[skills_col]):
            skills_str = str(row[skills_col]).strip()
            # Split by comma or semicolon
            skills_value = [s.strip() for s in skills_str.replace(";", ",").split(",")]

        return {
            "raw_text": activity_text,
            "metadata": {
                "source": "excel",
                "row_number": row_number,
                "date": date_value,
                "hours": hours_value,
                "skills": skills_value,
                "original_row": row.to_dict()
            }
        }
