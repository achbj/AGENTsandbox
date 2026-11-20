import shutil
import subprocess
import sys
import tempfile

SAFE_ENV = {
    "PATH": "/usr/bin:/bin",
    "PYTHONDONTWRITEBYTECODE": "1",
}

def run_agent_code(code: str, timeout: int = 3) -> dict:
    """execute python code inside Linux network and PID namespace"""
    if sys.platform != "linux" or shutil.which("unshare") is None:
        raise RuntimeError("Level 3 requires Linux with the 'unshare' utility installed")

    
    with tempfile.TemporaryDirectory(prefix="lvl3_ns_") as workdir:
        cmd = [
            "unshare",
            "--net",
            "--pid",
            "--fork",
            "--mount-proc",
            sys.executable,
            "-c",
            code,
        ]
        try:
            proc = subprocess.run(
                cmd,
                cwd=workdir,
                env=SAFE_ENV,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            return {
                "exit_code": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr
            }
        except subprocess.TimeoutExpired:
            return {
                "exit_code": 124,
                "stdout": "",
                "stderr": f"Timeout after {timeout}s",
            }