#!/usr/bin/env python3
"""
Minimal diary automation: raw input -> AI format -> website submit -> email confirmation
"""
import os
import sys
import json
import smtplib
from email.message import EmailMessage
from pathlib import Path

from src.llm_client import get_llm_client
from src.diary_formatter import validate_and_format
from src.selenium_submit import VTUSubmitter
from src.utils.logger import get_logger

logger = get_logger(__name__)

def transform_to_form_data(entry_data: dict) -> dict:
    """Transform DiaryEntry to form data structure"""
    # Calculate total hours from activities
    total_minutes = 0
    for activity in entry_data.get("activities", []):
        duration = activity.get("duration_minutes")
        if duration:
            total_minutes += duration

    hours = total_minutes / 60 if total_minutes > 0 else 8  # Default 8 hours

    # Extract learnings from activities
    learnings = ", ".join([
        act["short_description"]
        for act in entry_data.get("activities", [])[:3]  # First 3 activities
    ]) or "Applied technical skills and problem-solving"

    # Extract blockers from uncertainties
    blockers = "; ".join(entry_data.get("uncertainties", [])) or "None"

    # Extract links from artifacts
    links = []
    for activity in entry_data.get("activities", []):
        for artifact in activity.get("artifacts", []):
            if artifact.startswith("http"):
                links.append(artifact)
    links_str = ", ".join(links) if links else "N/A"

    # Get skills from AI response (list of skill names)
    skills = entry_data.get("skills", ["Git"])  # Default to Git if not provided

    return {
        "date": entry_data["date"],
        "description": entry_data["entry_text"],
        "hours": round(hours, 1),
        "learnings": learnings,
        "blockers": blockers,
        "links": links_str,
        "skills": skills  # Pass as list for multi-select
    }

def send_email(to_email: str, subject: str, body: str):
    """Send email notification"""
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")

    if not smtp_user or not smtp_password:
        logger.warning("SMTP credentials not set, skipping email")
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = to_email
    msg.set_content(body)

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        logger.info(f"Email sent to {to_email}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")

def run_automation(raw_input_file: str, user_email: str):
    """Main automation flow"""

    # 1. Read raw input
    logger.info("Reading raw input...")
    raw_content = Path(raw_input_file).read_text(encoding="utf-8")

    # 2. AI structures it
    logger.info("Formatting with AI...")
    llm = get_llm_client()

    system_prompt = Path("system_prompts/diary_generator_system.txt").read_text()
    prompt = f"Transform this into a diary entry:\n\n{raw_content}"

    response = llm.generate(system=system_prompt, prompt=prompt)
    diary_data = json.loads(response)

    # Validate
    entry = validate_and_format(diary_data)
    logger.info(f"Generated entry for date: {entry.date}")

    # Transform to form data
    form_data = transform_to_form_data(diary_data)
    logger.info(f"Transformed to form data: {form_data['hours']} hours")

    # 3. Submit to website
    logger.info("Submitting to VTU portal...")
    submitter = VTUSubmitter(
        headless=os.getenv("SELENIUM_HEADLESS", "false").lower() == "true",
        wait_for_user=False
    )

    try:
        # Login
        portal_url = os.getenv("PORTAL_LOGIN_URL")
        submitter.login_manually(portal_url)

        # Fill and submit
        result = submitter.fill_diary(form_data, dry_run=False)

        if result == "SUBMITTED" or (isinstance(result, dict) and result.get("success")):
            logger.info("Submission successful!")

            # 4. Send email
            send_email(
                to_email=user_email,
                subject="Diary Entry Submitted",
                body=f"Your diary entry for {entry.date} has been submitted successfully.\n\nEntry text:\n{entry.entry_text}"
            )
        else:
            error_msg = result.get("error") if isinstance(result, dict) else str(result)
            logger.error(f"Submission failed: {error_msg}")
            send_email(
                to_email=user_email,
                subject="Diary Submission Failed",
                body=f"Failed to submit diary entry: {error_msg}"
            )
    finally:
        submitter.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python main.py <input_file> <your_email>")
        sys.exit(1)

    input_file = sys.argv[1]
    user_email = sys.argv[2]

    run_automation(input_file, user_email)
