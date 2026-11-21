# Level 4: Bubblewrap Isolation (`bwrap`)

Builds a restricted root view using unprivileged `bubblewrap` (`bwrap`) with `--unshare-all`, `--unshare-net`, read-only system mounts (`--ro-bind`), a fresh `/dev` and `/proc`, a `/tmp` `tmpfs`, and a single read-write `/workspace` bind mount.

## What Changed vs. Level 3

- **Curated root filesystem:** Only `/usr`, `/bin`, `/lib` (and `/lib64` if present) are mounted read-only; host `/home` and `/etc` are not exposed.
- **Scoped writable storage:** Only `/workspace` (backed by an ephemeral host temp directory) and `/tmp` are writable.
- **Full namespace isolation:** Combines user/mount/PID/IPC/UTS/net isolation with `--die-with-parent` and `--new-session`.

## Remaining Gaps (Why Level 5 Is Needed)

| Bypass / Limitation         | Why It Still Happens                                                | Addressed In                                        |
| :-------------------------- | :------------------------------------------------------------------ | :-------------------------------------------------- |
| **Risky syscalls**          | `bwrap` sets up namespaces/mounts, not a syscall denylist/allowlist | Level 5 (`--seccomp <fd>`)                          |
| **Memory / CPU exhaustion** | Unbounded allocations or tight CPU loops can still strain resources | Level 5 (`RLIMIT_AS`, `RLIMIT_CPU`, `RLIMIT_NPROC`) |
