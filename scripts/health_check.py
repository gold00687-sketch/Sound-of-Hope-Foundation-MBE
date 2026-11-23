"""Simple HTTP health check script for Docker and CI use.

Usage:
    python scripts/health_check.py
Exits 0 if healthy, 1 otherwise.
"""

import sys
import urllib.request

URL = "http://localhost:8000/health"

try:
    with urllib.request.urlopen(URL, timeout=5) as response:
        if response.status == 200:
            print("OK")
            sys.exit(0)
        print(f"Unexpected status: {response.status}")
        sys.exit(1)
except Exception as exc:
    print(f"Health check failed: {exc}")
    sys.exit(1)
