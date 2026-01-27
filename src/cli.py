#!/usr/bin/env python3
"""
VTU Internship Automation CLI
"""
import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from commands import cmd_generate, cmd_submit, cmd_serve, cmd_audit, cmd_validate

def main():
    parser = argparse.ArgumentParser(description="VTU Internship Diary Automation")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Generate
    p_gen = subparsers.add_parser("generate", help="Generate diary")
    p_gen.add_argument("--input", "-i", default="-")
    p_gen.add_argument("--output", "-o")
    p_gen.add_argument("--with-git", action="store_true")
    p_gen.add_argument("--git-repo")
    p_gen.add_argument("--with-calendar", action="store_true")
    p_gen.set_defaults(func=cmd_generate)
    
    # Submit
    p_sub = subparsers.add_parser("submit", help="Submit to portal")
    p_sub.add_argument("--entry", "-e", required=True)
    p_sub.add_argument("--dry-run", action="store_true")
    p_sub.add_argument("--headless", action="store_true")
    p_sub.add_argument("--skip-login", action="store_true")
    p_sub.add_argument("--keep-browser", action="store_true")
    p_sub.add_argument("--hours", type=int)
    p_sub.add_argument("--learnings")
    p_sub.add_argument("--blockers")
    p_sub.add_argument("--skill-ids")
    p_sub.set_defaults(func=cmd_submit)
    
    # Serve
    p_serve = subparsers.add_parser("serve", help="Start web UI")
    p_serve.add_argument("--host", default="127.0.0.1")
    p_serve.add_argument("--port", "-p", type=int, default=5000)
    p_serve.set_defaults(func=cmd_serve)
    
    # Audit
    p_audit = subparsers.add_parser("audit", help="Audit logs")
    p_audit.add_argument("action", choices=["list", "export", "rotate", "clear"])
    p_audit.add_argument("--output", "-o")
    p_audit.set_defaults(func=cmd_audit)
    
    # Validate
    p_val = subparsers.add_parser("validate", help="Validate config")
    p_val.set_defaults(func=cmd_validate)
    
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
        
    args.func(args)

if __name__ == "__main__":
    main()
