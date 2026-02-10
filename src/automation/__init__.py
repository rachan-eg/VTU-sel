"""Browser automation and parallel submission"""
from .selenium_submission_engine import SeleniumSubmissionEngine as ParallelSubmissionEngine
from .retry_logic import RetryStrategy

# Legacy Playwright engine (has Windows issues)
# from .submission_engine import ParallelSubmissionEngine

__all__ = ["ParallelSubmissionEngine", "RetryStrategy"]
