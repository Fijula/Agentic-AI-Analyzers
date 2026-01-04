"""
Script to clear/delete Jira issues.

Usage:
    # Delete a specific issue
    python -m src.integrations.jira_clear --delete QA-1
    
    # Delete multiple issues
    python -m src.integrations.jira_clear --delete QA-1 QA-2 QA-3
    
    # Reset entire database (clears all issues)
    python -m src.integrations.jira_clear --reset
    
    # List all issues
    python -m src.integrations.jira_clear --list
"""
from __future__ import annotations
import os
import argparse
import sys
from typing import Any, Dict, List
from src.core.utils import http_get_json, http_post_json
import requests

JIRA_BASE = os.getenv("JIRA_BASE", "http://localhost:4001")
JIRA_BEARER = os.getenv("JIRA_BEARER") or "demo-token"


def get_headers() -> Dict[str, str]:
    """Get authorization headers."""
    return {"Authorization": f"Bearer {JIRA_BEARER}"}


def list_issues(max_results: int = 100) -> List[Dict[str, Any]]:
    """List all issues in Jira."""
    url = f"{JIRA_BASE}/rest/api/3/search"
    params = {"maxResults": max_results}
    headers = get_headers()
    
    try:
        response = http_get_json(url, params=params, headers=headers)
        issues = response.get("issues", [])
        return issues
    except Exception as e:
        print(f"❌ Failed to list issues: {e}", file=sys.stderr)
        return []


def delete_issue(issue_key: str) -> bool:
    """Delete a single issue by key."""
    url = f"{JIRA_BASE}/rest/api/3/issue/{issue_key}"
    headers = get_headers()
    
    try:
        r = requests.delete(url, headers=headers, timeout=60)
        r.raise_for_status()
        print(f"✅ Deleted issue: {issue_key}")
        return True
    except Exception as e:
        print(f"❌ Failed to delete {issue_key}: {e}", file=sys.stderr)
        return False


def reset_database() -> bool:
    """Reset the entire Jira database (admin operation)."""
    url = f"{JIRA_BASE}/admin/reset"
    headers = get_headers()
    
    try:
        response = http_post_json(url, {}, headers=headers)
        if response.get("status") == "reset":
            print("✅ Database reset successfully")
            return True
        else:
            print(f"⚠️ Unexpected response: {response}", file=sys.stderr)
            return False
    except Exception as e:
        print(f"❌ Failed to reset database: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Clear/delete Jira issues",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        "--delete",
        nargs="+",
        metavar="ISSUE_KEY",
        help="Delete one or more issues by key (e.g., QA-1 QA-2)"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset entire database (clears all issues)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all issues"
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=100,
        help="Maximum results when listing (default: 100)"
    )
    
    args = parser.parse_args()
    
    if not any([args.delete, args.reset, args.list]):
        parser.print_help()
        sys.exit(1)
    
    # List issues
    if args.list:
        print(f"📋 Listing issues from {JIRA_BASE}...")
        issues = list_issues(max_results=args.max_results)
        if not issues:
            print("No issues found.")
        else:
            print(f"\nFound {len(issues)} issue(s):\n")
            for issue in issues:
                key = issue.get("key", "UNKNOWN")
                summary = issue.get("fields", {}).get("summary", "No summary")
                print(f"  • {key}: {summary}")
        return
    
    # Delete specific issues
    if args.delete:
        print(f"🗑️  Deleting {len(args.delete)} issue(s)...")
        success_count = 0
        for issue_key in args.delete:
            if delete_issue(issue_key):
                success_count += 1
        print(f"\n✅ Successfully deleted {success_count}/{len(args.delete)} issue(s)")
        return
    
    # Reset database
    if args.reset:
        print("⚠️  Resetting entire database...")
        confirm = input("This will delete ALL issues. Continue? (yes/no): ")
        if confirm.lower() in ("yes", "y"):
            reset_database()
        else:
            print("❌ Reset cancelled")


if __name__ == "__main__":
    main()

