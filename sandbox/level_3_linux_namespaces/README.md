# Level 3: Linux Namespaces (`unshare`)

Runs code inside Linux kernel namespaces on a Linux host using `unshare --net --pid --fork --mount-proc` alongside a scrubbed environment and temporary `cwd`.

## What Changed vs. Level 2

- **Network namespace (`--net`):** Detaches the network stack so outbound internet/LAN connections fail by default.
- **PID namespace + `/proc` mount (`--pid --fork --mount-proc`):** Hides host processes so the child only sees PIDs inside its own namespace.

## Remaining Gaps (Why Level 4 Is Needed)

| Bypass / Limitation          | Why It Still Happens                                                            | Addressed In                             |
| :--------------------------- | :------------------------------------------------------------------------------ | :--------------------------------------- |
| **Unfiltered host `/` tree** | Without a custom root or bind mounts, host directories remain visible/reachable | Level 4 (`bwrap` `--ro-bind` & `--bind`) |
| **No syscall filtering**     | All syscalls allowed by the host kernel remain reachable                        | Level 5 (`seccomp` BPF)                  |
| **No resource limits**       | Memory/CPU/process spikes aren't capped yet                                     | Level 5 (`setrlimit`)                    |
