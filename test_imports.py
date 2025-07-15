#!/usr/bin/env python3
"""Test script to identify what's causing the hang"""

import sys
import os

print("Step 1: Basic Python works")

try:
    import json
    print("Step 2: json import OK")
except Exception as e:
    print(f"Step 2 FAILED: {e}")
    sys.exit(1)

try:
    import time
    print("Step 3: time import OK")
except Exception as e:
    print(f"Step 3 FAILED: {e}")
    sys.exit(1)

try:
    import argparse
    print("Step 4: argparse import OK")
except Exception as e:
    print(f"Step 4 FAILED: {e}")
    sys.exit(1)

try:
    import logging
    print("Step 5: logging import OK")
except Exception as e:
    print(f"Step 5 FAILED: {e}")
    sys.exit(1)

try:
    import hashlib
    print("Step 6: hashlib import OK")
except Exception as e:
    print(f"Step 6 FAILED: {e}")
    sys.exit(1)

try:
    from typing import List, Dict, Optional, Tuple
    print("Step 7: typing import OK")
except Exception as e:
    print(f"Step 7 FAILED: {e}")
    sys.exit(1)

try:
    from concurrent.futures import ThreadPoolExecutor, as_completed
    print("Step 8: concurrent.futures import OK")
except Exception as e:
    print(f"Step 8 FAILED: {e}")
    sys.exit(1)

try:
    from functools import wraps
    print("Step 9: functools import OK")
except Exception as e:
    print(f"Step 9 FAILED: {e}")
    sys.exit(1)

try:
    from dataclasses import dataclass
    print("Step 10: dataclasses import OK")
except Exception as e:
    print(f"Step 10 FAILED: {e}")
    sys.exit(1)

print("Step 11: About to import requests...")
try:
    import requests
    print("Step 12: requests import OK")
except Exception as e:
    print(f"Step 12 FAILED: {e}")
    sys.exit(1)

print("Step 13: About to import tqdm...")
try:
    from tqdm import tqdm
    print("Step 14: tqdm import OK")
except Exception as e:
    print(f"Step 14 FAILED: {e}")
    sys.exit(1)

print("Step 15: About to import config...")
try:
    from config import INS_API_KEY
    print("Step 16: config import OK")
except Exception as e:
    print(f"Step 16 FAILED: {e}")
    print("Using environment variable instead...")

print("ALL IMPORTS SUCCESSFUL!")
print("Test completed successfully!")
