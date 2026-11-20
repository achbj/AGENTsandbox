from runner import run_agent_code

ATTACKS = {
    "1. Network Egress Blocked by NetNS": """
import urllib.request
try:
    with urllib.request.urlopen("https://example.com", timeout=2) as resp:
        print("LEAKED HTTP:", resp.status)
except Exception as e:
    print("Blocked as expected:", type(e).__name__, e)
""",
    "2. PID Namespace Isolation Check": """
import os
from pathlib import Path
print("Own PID inside namespace:", os.getpid())
proc_pids = sorted(p.name for p in Path("/proc").iterdir() if p.name.isdigit())
print("Visible /proc PIDs:", proc_pids)
""",
    "3. Host Root Still Unfiltered (Why Level 4 Is Needed)": """
from pathlib import Path
print("Top-level / entries:", sorted(p.name for p in Path("/").iterdir())[:10])
""",
}

if __name__ == "__main__":
    for title, payload in ATTACKS.items():
        print(f"=== {title} ===")
        res = run_agent_code(payload)
        print(res["stdout"].strip() or res["stderr"].strip())
        print()