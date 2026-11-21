import os
from pathlib import Path
import shutil
import subprocess
import tempfile

SAFE_ENV_KEYS = {"PATH", "TERM", "LANG", "LC_ALL"}


def _build_clean_env(workspace_dir: str, claude_dir: str) -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if k in SAFE_ENV_KEYS}
    env["HOME"] = workspace_dir
    env["CLAUDE_CONFIG_DIR"] = claude_dir
    if os.environ.get("ANTHROPIC_API_KEY"):
        env["ANTHROPIC_API_KEY"] = os.environ["ANTHROPIC_API_KEY"]
    return env


def run_claude_mac_sandbox(
    prompt: str,
    claude_dir: str | None = None,
    timeout: int = 45,
) -> dict:
    claude_bin = shutil.which("claude")
    profile_path = Path(__file__).with_name("claude_profile.sb").resolve()
    if not claude_bin:
        raise RuntimeError("`claude` CLI not found in PATH.")

    home_resolved = str(Path.home().resolve())
    effective_claude_dir = str(Path(claude_dir).resolve()) if claude_dir else str((Path.home() / ".claude").resolve())

    with tempfile.TemporaryDirectory(prefix="claude_mac_ws_") as raw_workdir:
        workdir = str(Path(raw_workdir).resolve())
        Path(workdir, "notes.txt").write_text("Alpha\nBeta\nGamma\n", encoding="utf-8")

        cmd = [
            "/usr/bin/sandbox-exec",
            "-f",
            str(profile_path),
            f"-DHOME_DIR={home_resolved}",
            f"-DCLAUDE_DIR={effective_claude_dir}",
            f"-DWORKSPACE_DIR={workdir}",
            claude_bin,
            "-p",
            prompt,
        ]

        try:
            proc = subprocess.run(
                cmd,
                cwd=workdir,
                env=_build_clean_env(workdir, effective_claude_dir),
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return {
                "exit_code": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "workspace_files": sorted(p.name for p in Path(workdir).iterdir()),
            }
        except subprocess.TimeoutExpired:
            return {
                "exit_code": 124,
                "stdout": "",
                "stderr": f"Timed out after {timeout}s",
                "workspace_files": sorted(p.name for p in Path(workdir).iterdir()),
            }