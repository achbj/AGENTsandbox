import os
from pathlib import Path
import resource
import shutil
import subprocess
import sys
import tempfile

from seccomp_filter import build_bpf_filter_bytes

SAFE_ENV = {
    "PATH": "/usr/local/bin:/usr/bin:/bin",
    "PYTHONDONTWRITEBYTECODE": "1",
    "HOME": "/workspace",
}


def _apply_resource_limits(mem_mb: int = 256, cpu_sec: int = 3, max_procs: int = 16):
    mem_bytes = mem_mb * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_CPU, (cpu_sec, cpu_sec))
    resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))
    try:
        resource.setrlimit(resource.RLIMIT_NPROC, (max_procs, max_procs))
    except (ValueError, OSError):
        pass


def run_agent_code(code: str, timeout: int = 3, mem_mb: int = 256) -> dict:
    """Execute Python code in bwrap with seccomp syscall filtering and rlimits."""
    if sys.platform != "linux" or shutil.which("bwrap") is None:
        raise RuntimeError("Level 5 requires Linux with `bwrap` installed.")

    bpf_bytes = build_bpf_filter_bytes()
    read_fd, write_fd = os.pipe()

    try:
        os.write(write_fd, bpf_bytes)
        os.close(write_fd)
        write_fd = -1

        with tempfile.TemporaryDirectory(prefix="lvl5_ws_") as workdir:
            cmd = [
                "bwrap",
                "--unshare-all",
                "--unshare-net",
                "--die-with-parent",
                "--new-session",
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
                "--bind", workdir, "/workspace",
                "--chdir", "/workspace",
                "--seccomp", str(read_fd),
                "--clearenv",
            ])
            for k, v in SAFE_ENV.items():
                cmd.extend(["--setenv", k, v])

            cmd.extend([sys.executable, "-c", code])

            try:
                proc = subprocess.run(
                    cmd,
                    pass_fds=(read_fd,),
                    preexec_fn=lambda: _apply_resource_limits(mem_mb=mem_mb, cpu_sec=timeout),
                    capture_output=True,
                    text=True,
                    timeout=timeout + 1,
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
    finally:
        if read_fd >= 0:
            try:
                os.close(read_fd)
            except OSError:
                pass
        if write_fd >= 0:
            try:
                os.close(write_fd)
            except OSError:
                pass