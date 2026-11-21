# Level 5: Airtight `bubblewrap` + `seccomp` + Resource Limits

Combines the Level 4 `bubblewrap` isolation profile with a compiled `libseccomp` BPF filter (`seccomp_filter.py`, passed via pipe FD to `bwrap --seccomp`) and per-process `resource.setrlimit` caps (`RLIMIT_AS`, `RLIMIT_CPU`, `RLIMIT_NPROC`).

## What Changed vs. Level 4

- **Syscall filtering (`seccomp`):** Blocks high-risk kernel syscalls (such as `ptrace`, `mount`, `umount2`, `pivot_root`, `reboot`, `bpf`, `userfaultfd`, module loading) with `EPERM`.
- **Resource bounds (`setrlimit`):** Caps virtual address space (`RLIMIT_AS`), CPU seconds (`RLIMIT_CPU`), and process count (`RLIMIT_NPROC`) on each run.

## Practical Caveats

- `RLIMIT_AS` limits virtual address space (which can be tight for runtimes that reserve large virtual mappings), so tune `mem_mb` to your workload and test carefully.
- For multi-tenant production workloads, pair this with cgroup v2 enforcement or a stronger isolation boundary (such as a microVM or gVisor) depending on threat model.
