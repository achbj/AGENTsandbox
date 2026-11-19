# Level 1: Basic Subprocess (`subprocess.run`)

after running [test_attacks.py](../../proofs/test_attacks.py) we learn that it inherited my whole mac shell environment `$Home` and `~/.ssh`.
Executes untrusted Python code via `subprocess.run([sys.executable, "-c", code], timeout=...)`.
Prevents crashes and infinite loops, but provides **zero isolation**.

## Verified Vulnerabilities

| Attack Vector        | What Exposed / Succeeded                                           | Root Cause                                             | Target Level to Mitigate                                   |
| :------------------- | :----------------------------------------------------------------- | :----------------------------------------------------- | :--------------------------------------------------------- |
| **Filesystem Recon** | Listed `$HOME` and `~/.ssh` keys (`id_rsa`, `lightning_rsa`, etc.) | Inherits user UID and full host filesystem permissions | Level 2 (scoped workspace) / Level 4 (`bwrap` bind mounts) |
| **Env Secret Leak**  | Read `os.environ`, including `PROD_DATABASE_URL`                   | Child inherits parent process environment by default   | Level 2 (explicit allowlisted `env` dict)                  |
| **Network Egress**   | Reached `https://example.com` (`HTTP 200`)                         | Shares host network stack / default routing            | Level 3 (`unshare -n`) / Level 4 (`bwrap --unshare-net`)   |
