"""Parallel submission engine using Playwright multi-context"""
import asyncio
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path

try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

from config import (
    MAX_PARALLEL_BROWSERS,
    SUBMISSION_DELAY_SECONDS,
    HEADLESS,
    SCREENSHOTS_DIR,
    ENABLE_SCREENSHOTS,
    PORTAL_LOGIN_URL,
    VTU_USERNAME,
    VTU_PASSWORD
)
from src.utils.logger import get_logger
from .retry_logic import RetryStrategy

logger = get_logger(__name__)


class ParallelSubmissionEngine:
    """
    High-performance parallel submission engine.

    Uses Playwright with multiple browser contexts for concurrent submissions.
    """

    def __init__(self, max_workers: int = MAX_PARALLEL_BROWSERS, headless: bool = HEADLESS):
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright required. Install with: pip install playwright")

        self.max_workers = max_workers
        self.headless = headless
        self.submission_queue = asyncio.Queue()
        self.results = []
        self.retry_strategy = RetryStrategy()

        logger.info(f"Parallel engine initialized: {max_workers} workers, headless={headless}")

    async def submit_bulk(self, entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Submit multiple diary entries concurrently.

        Args:
            entries: List of entry dicts with date, hours, activities, etc.

        Returns:
            List of result dicts with status and metadata
        """
        logger.info(f"Starting bulk submission: {len(entries)} entries")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)

            try:
                # Create worker tasks
                workers = [
                    asyncio.create_task(self._worker(browser, worker_id))
                    for worker_id in range(self.max_workers)
                ]

                # Enqueue all entries
                for entry in entries:
                    await self.submission_queue.put(entry)

                # Wait for completion
                await self.submission_queue.join()

                # Cancel workers
                for w in workers:
                    w.cancel()

            finally:
                await browser.close()

        logger.info(f"Bulk submission complete: {len(self.results)} results")
        return self.results

    async def _worker(self, browser: Browser, worker_id: int):
        """Worker coroutine that processes submissions"""
        context = await browser.new_context()
        page = await context.new_page()

        # Login to portal
        try:
            await self._login(page)
            logger.info(f"Worker {worker_id} logged in successfully")
        except Exception as e:
            logger.error(f"Worker {worker_id} login failed: {e}")
            await context.close()
            return

        logger.info(f"Worker {worker_id} started")

        while True:
            try:
                # Get entry from queue (with timeout to allow cancellation)
                try:
                    entry = await asyncio.wait_for(
                        self.submission_queue.get(),
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue

                logger.info(f"Worker {worker_id} processing: {entry.get('date')}")

                # Submit with retry logic
                result = await self.retry_strategy.retry_with_backoff(
                    self._submit_entry,
                    page,
                    entry
                )

                self.results.append(result)

                # Rate limiting
                await asyncio.sleep(SUBMISSION_DELAY_SECONDS)

            except asyncio.CancelledError:
                logger.info(f"Worker {worker_id} cancelled")
                break

            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
                self.results.append({
                    "date": entry.get("date"),
                    "status": "failed",
                    "error": str(e)
                })

            finally:
                self.submission_queue.task_done()

        await context.close()

    async def _submit_entry(self, page: Page, entry: Dict[str, Any]) -> Dict[str, Any]:
        """Submit single diary entry"""
        date_str = entry.get("date", "unknown")

        try:
            # Navigate to diary page
            await page.goto(f"{PORTAL_LOGIN_URL}/diary", wait_until="networkidle")

            # Fill form
            await self._fill_form(page, entry)

            # Screenshot before submit
            if ENABLE_SCREENSHOTS:
                screenshot_path = SCREENSHOTS_DIR / f"{date_str}_pre.png"
                await page.screenshot(path=str(screenshot_path))

            # Submit
            await page.click("button[type='submit']")
            await page.wait_for_load_state("networkidle")

            # Verify success
            success = await self._verify_submission(page)

            # Screenshot after submit
            if ENABLE_SCREENSHOTS:
                await page.screenshot(path=str(SCREENSHOTS_DIR / f"{date_str}_post.png"))

            return {
                "date": date_str,
                "status": "success" if success else "unknown",
                "submitted_at": datetime.now().isoformat(),
                "entry": entry
            }

        except Exception as e:
            logger.error(f"Submission failed for {date_str}: {e}")
            raise

    async def _fill_form(self, page: Page, entry: Dict[str, Any]):
        """Fill diary form fields"""

        # Date
        if "date" in entry:
            await page.fill("input[name='date'], input[type='date']", entry["date"])

        # Hours
        if "hours" in entry:
            await page.fill("input[name='hours'], input[type='number']", str(entry["hours"]))

        # Activities/Description
        if "activities" in entry:
            await page.fill(
                "textarea[name='description'], textarea[name='entry_text']",
                entry["activities"]
            )

        # Learnings
        if "learnings" in entry:
            await page.fill("textarea[name='learnings']", entry["learnings"])

        # Blockers
        if "blockers" in entry:
            await page.fill("textarea[name='blockers']", entry.get("blockers", "None"))

        # Links
        if "links" in entry:
            await page.fill("input[name='links']", entry.get("links", ""))

        # Skills (multi-select)
        if "skills" in entry and entry["skills"]:
            await self._select_skills(page, entry["skills"])

    async def _select_skills(self, page: Page, skills: List[str]):
        """Select multiple skills from React Select dropdown"""
        for skill in skills:
            try:
                # Find input
                skill_input = page.locator("input[id^='react-select-']").first

                # Click to open
                await skill_input.click()
                await asyncio.sleep(0.3)

                # Type skill name
                await skill_input.fill(skill)
                await asyncio.sleep(0.5)

                # Press Enter to select
                await skill_input.press("Enter")
                await asyncio.sleep(0.3)

            except Exception as e:
                logger.warning(f"Failed to select skill '{skill}': {e}")

    async def _verify_submission(self, page: Page) -> bool:
        """Verify submission was successful"""
        try:
            # Look for success message
            success_locator = page.locator(".success-message, .alert-success")
            await success_locator.wait_for(timeout=5000)
            return True
        except:
            logger.warning("Could not verify submission success")
            return False

    async def _login(self, page: Page):
        """Login to VTU portal using actual form selectors"""
        if not VTU_USERNAME or not VTU_PASSWORD:
            raise ValueError("VTU_USERNAME and VTU_PASSWORD must be set in environment")

        logger.info(f"Logging in to {PORTAL_LOGIN_URL}")

        try:
            # Navigate to login page
            await page.goto(PORTAL_LOGIN_URL, wait_until="networkidle")

            # Fill email field (using actual VTU portal selectors)
            email_selectors = [
                "input[autocomplete='email']",
                "input[type='email']",
                "input#email",
                "input[name='email']"
            ]

            email_filled = False
            for selector in email_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    await page.fill(selector, VTU_USERNAME)
                    email_filled = True
                    logger.info(f"Filled email with selector: {selector}")
                    break
                except:
                    continue

            if not email_filled:
                raise Exception("Could not find email field")

            # Fill password field
            password_selectors = [
                "input[autocomplete='new-password']",
                "input[autocomplete='current-password']",
                "input[type='password']",
                "input#password",
                "input[name='password']"
            ]

            password_filled = False
            for selector in password_selectors:
                try:
                    await page.fill(selector, VTU_PASSWORD)
                    password_filled = True
                    logger.info(f"Filled password with selector: {selector}")
                    break
                except:
                    continue

            if not password_filled:
                raise Exception("Could not find password field")

            # Click submit button
            await page.click("button[type='submit']")
            await asyncio.sleep(3)  # Wait for login to process
            await page.wait_for_load_state("networkidle")

            # Verify login success
            current_url = page.url
            if "sign-in" in current_url.lower() or "login" in current_url.lower():
                # Check for error messages
                try:
                    error = await page.locator("text=/Invalid|failed/i").first.text_content()
                    raise Exception(f"Login failed: {error}")
                except:
                    raise Exception("Login failed - still on login page")

            logger.info("Login successful")

        except Exception as e:
            logger.error(f"Login failed: {e}")
            raise

    async def _load_session(self, context: BrowserContext):
        """Load saved session cookies/state"""
        # TODO: Load session from file
        pass
