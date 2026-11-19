from pathlib import Path
import subprocess
import sys
import tempfile

"""
# New word for me
    - scrubbed env: env that has be cleaned of potentially sensitive, unnecessary or inhereted information before process starts
"""
SAFE_ENV = {
    "PATH": "usr/bin:/bin",
    "PYTHONDONTWRITEBYTECODE": "1",
}

def run_agent_code(code: str, timeout: int = 3) -> dict:
    """execute python code with a scrubbed env and isolated temp cwd"""
    with tempfile.TemporaryDirectory(prefix="lvl2_sandbox_") as workdir:
        try:
            proc = subprocess.run(
                [sys.executable, "-c", code],
                cwd=workdir,
                env=SAFE_ENV,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            return {
                "exit_code": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "workdir": workdir,
            }
        except subprocess.TimeoutExpired:
            return {
                "exit_code": 124,
                "stdout": "",
                "stderr": f"Timeout after {timeout}s",
                "workdir": workdir,
            }