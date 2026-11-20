from runner import run_agent_code

ATTACKS = {
    "1. Host /home & /etc Absent": """
from pathlib import Path
print("Top-level / entries:", sorted(p.name for p in Path("/").iterdir()))
print("/home exists?:", Path("/home").exists())
print("/etc exists?:", Path("/etc").exists())
""",
    "2. Read-Only System Mount Enforcement": """
from pathlib import Path
try:
    Path("/usr/evil_file.txt").write_text("pwned")
    print("LEAKED: Wrote to /usr")
except OSError as e:
    print("Blocked writing to /usr:", type(e).__name__, e)
""",
    "3. Workspace Write Allowed & Scoped": """
from pathlib import Path
f = Path("/workspace/output.txt")
f.write_text("ok")
print("Wrote /workspace/output.txt:", f.read_text(), "cwd:", Path.cwd())
""",
    "4. Network Still Blocked": """
import urllib.request
try:
    with urllib.request.urlopen("https://example.com", timeout=2) as resp:
        print("LEAKED HTTP:", resp.status)
except Exception as e:
    print("Blocked network:", type(e).__name__, e)
""",
}

if __name__ == "__main__":
    for title, payload in ATTACKS.items():
        print(f"=== {title} ===")
        res = run_agent_code(payload)
        print(res["stdout"].strip() or res["stderr"].strip())
        print()