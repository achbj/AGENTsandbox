from pathlib import Path
import subprocess
import sys

def run_agent_code(code: str, timeout: int = 3) -> dict:
    """Execute python code in a child subprocess with a timeout"""
    try:
        proc = subprocess.run(
            [sys.executable, "-c", code],
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
            "stderr": f"Timeout after {timeout}s" 
          }



if __name__ == "__main__":
    code_str = Path("agent_code.py").read_text(encoding="utf-8")
    res = run_agent_code(code_str)
    print(f"-- EXIT CODE: {res['exit_code']} --")
    print(f"STDOUT: \n{res['stdout'].strip()}\n")
    print(f"STDERR: \n{res['stderr'].strip()}")