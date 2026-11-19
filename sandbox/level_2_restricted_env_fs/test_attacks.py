import os
from runner import run_agent_code

os.environ["PROD_DATABASE_URL"] = "postgres://admin:SuperSecret123@db.internal:5432/prod"

ATTACKS = {
    "1. Env Secret Scrubbing Check": """
import os
print("PROD_DATABASE_URL present?:", "PROD_DATABASE_URL" in os.environ)
print("Env keys visible:", list(os.environ.keys()))
""",
    "2. Ephemeral CWD Isolation Check": """
from pathlib import Path
Path("leaked_artifact.txt").write_text("hello")
print("Current working dir:", Path.cwd())
print("Files in cwd:", [p.name for p in Path.cwd().iterdir()])
""",
    "3. Absolute Path Bypass (Still Vulnerable)": """
import os
from pathlib import Path
# Fallback if HOME was stripped from env; works on Linux/macOS depending on permissions
target = Path(os.path.expanduser("~"))
print("Target home:", target)
print("Exists & readable?:", target.exists(), os.access(target, os.R_OK))
""",
    "4. Network Egress (Still Vulnerable)": """
import urllib.request
req = urllib.request.Request("https://example.com", method="HEAD")
with urllib.request.urlopen(req, timeout=2) as resp:
    print(f"Outbound connection succeeded! HTTP Status: {resp.status}")
""",
}

if __name__ == "__main__":
    for title, payload in ATTACKS.items():
        print(f"=== {title} ===")
        result = run_agent_code(payload)
        print(result["stdout"].strip() or result["stderr"].strip())
        print()