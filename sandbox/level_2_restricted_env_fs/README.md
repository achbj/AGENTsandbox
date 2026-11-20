# Level 2: Restricted Environment & Scoped Workspace

Executes Python code with a minimal allowlisted environment (`SAFE_ENV`) and an ephemeral temporary working directory (`tempfile.TemporaryDirectory`) that is deleted after execution.

## What Changed vs. Level 1

- **Environment scrubbing:** Strips inherited shell variables and secrets (`PROD_DATABASE_URL`, tokens, user paths) unless explicitly passed in `SAFE_ENV`.
- **Ephemeral `cwd`:** Sets `cwd` to a fresh temporary directory per run so relative writes do not persist in the repo or host project folder.

## Remaining Gaps (Why Level 3 Is Needed)

| Bypass / Limitation                    | Why It Still Happens                                                                 | Addressed In                        |
| :------------------------------------- | :----------------------------------------------------------------------------------- | :---------------------------------- |
| **Absolute path access**               | Code can still reference `/Users/...`, `/home/...`, or other readable paths directly | Level 4 (`bwrap` curated mounts)    |
| **Outbound network**                   | Shares the host network stack and default routes                                     | Level 3 (`unshare --net`) / Level 4 |
| **No PID / syscall / resource limits** | No kernel namespace isolation, syscall filtering, or memory/CPU caps                 | Levels 3 & 5                        |
