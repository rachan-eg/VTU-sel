#!/usr/bin/env python3
"""Quick test to verify setup is working"""
import os
import sys
from pathlib import Path

def test_env_vars():
    """Check required environment variables"""
    print("Checking environment variables...")

    required = {
        "LLM_PROVIDER": os.getenv("LLM_PROVIDER"),
        "PORTAL_LOGIN_URL": os.getenv("PORTAL_LOGIN_URL"),
    }

    optional = {
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "VTU_EMAIL": os.getenv("VTU_EMAIL"),
        "VTU_PASSWORD": os.getenv("VTU_PASSWORD"),
        "SMTP_USER": os.getenv("SMTP_USER"),
        "SMTP_PASSWORD": os.getenv("SMTP_PASSWORD"),
    }

    missing = []
    for key, val in required.items():
        if not val:
            missing.append(key)
            print(f"  ✗ {key} - MISSING")
        else:
            print(f"  ✓ {key} - OK")

    for key, val in optional.items():
        if val:
            print(f"  ✓ {key} - OK")
        else:
            print(f"  ⚠ {key} - Not set (optional)")

    if missing:
        print(f"\nERROR: Missing required variables: {', '.join(missing)}")
        return False

    return True

def test_imports():
    """Check Python dependencies"""
    print("\nChecking imports...")

    try:
        from src.llm_client import get_llm_client
        print("  ✓ llm_client")

        from src.diary_formatter import validate_and_format
        print("  ✓ diary_formatter")

        from src.selenium_submit import VTUSubmitter
        print("  ✓ selenium_submit")

        import selenium
        print("  ✓ selenium")

        return True
    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        print("\nRun: pip install -r requirements.txt")
        return False

def test_files():
    """Check required files exist"""
    print("\nChecking files...")

    files = [
        "system_prompts/diary_generator_system.txt",
        "input/raw_input.txt",
        ".env.docker",
    ]

    missing = []
    for f in files:
        if Path(f).exists():
            print(f"  ✓ {f}")
        else:
            missing.append(f)
            print(f"  ✗ {f} - MISSING")

    if missing:
        print(f"\nWARNING: Missing files: {', '.join(missing)}")
        return False

    return True

def main():
    print("=" * 50)
    print("VTU Diary Automation - Setup Test")
    print("=" * 50)

    results = [
        test_files(),
        test_imports(),
        test_env_vars(),
    ]

    print("\n" + "=" * 50)
    if all(results):
        print("✓ All checks passed! Ready to run.")
        print("\nNext step: python main.py input/raw_input.txt your_email@example.com")
        return 0
    else:
        print("✗ Some checks failed. Fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
