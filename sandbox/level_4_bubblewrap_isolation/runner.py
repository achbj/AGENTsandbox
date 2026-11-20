from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

SAFE_ENV = {
    "PATH": "/usr/local/bin:/usr/bin:/bin",
    "PYTHONDONTWRITEBYTECODE": "1",
    "HOME": "/workspace",
}


def run_agent_code(code: str, timeout: int = 3) -> dict:
    """execute Python code inside a bubblewrap mount/net/pid/ipc/uts sandbox."""
    if sys.platform != "linux" or shutil.which("bwrap") is None:
        raise RuntimeError("Level 4 requires Linux with `bwrap` (bubblewrap) installed.")

    with tempfile.TemporaryDirectory(prefix="lvl4_ws_") as workdir:
        cmd = [
            "bwrap",
            "--unshare-all",
            "--share-net" if False else "--unshare-net",
            "--die-with-parent",
            "--new-session",
            # Read-only host OS directories needed for Python runtime
            "--ro-bind", "/usr", "/usr",
            "--ro-bind", "/bin", "/bin",
            "--ro-bind", "/lib", "/lib",
        ]
        if Path("/lib64").exists():
            cmd.extend(["--ro-bind", "/lib64", "/lib64"])

        cmd.extend([
            "--dev", "/dev",
            "--proc", "/proc",
            "--tmpfs", "/tmp",
            # Isolated read-write workspace mapped to /workspace
            "--bind", workdir, "/workspace",
            "--chdir", "/workspace",
            "--clearenv",
        ])
        for k, v in SAFE_ENV.items():
            cmd.extend(["--setenv", k, v])

        cmd.extend([sys.executable, "-c", code])

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return {
                "exit_code": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
            }
        except subprocess.TimeoutExpired:
            return {
                "exit_code": 124,
                "stdout": "",
                "stderr": f"Timeout after {timeout}s",
            }