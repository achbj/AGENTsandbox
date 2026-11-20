from runner import run_agent_code

ATTACKS = {
    "1. Blocked Dangerous Syscall via seccomp (ptrace)": """
import ctypes
libc = ctypes.CDLL("libc.so.6", use_errno=True)
# PTRACE_TRACEME = 0
rc = libc.ptrace(0, 0, 0, 0)
err = ctypes.get_errno()
print(f"ptrace return={rc}, errno={err} (1 = EPERM)")
""",
    "2. Memory Cap Enforcement (RLIMIT_AS)": """
try:
    # Attempt ~512MB allocation against 256MB limit
    chunks = [bytearray(64 * 1024 * 1024) for _ in range(8)]
    print("LEAKED: Allocated 512MB")
except MemoryError as e:
    print("Blocked by memory limit (MemoryError):", e)
""",
    "3. CPU / Infinite Loop Enforcement": """
x = 0
while True:
    x += 1
""",
    "4. Normal Safe Computation": """
nums = [i * i for i in range(10)]
print("Sum of squares 0..9:", sum(nums))
""",
}

if __name__ == "__main__":
    for title, payload in ATTACKS.items():
        print(f"=== {title} ===")
        res = run_agent_code(payload)
        print(f"exit={res['exit_code']} | out={res['stdout'].strip()!r} | err={res['stderr'].strip()[:140]!r}")
        print()