import io
import seccomp


def build_bpf_filter_bytes() -> bytes:
    """Compile a seccomp BPF filter blocking high-risk kernel syscalls."""
    # Default ALLOW for standard execution, explicitly return EPERM on dangerous syscalls
    flt = seccomp.SyscallFilter(defaction=seccomp.ALLOW)

    blocked_syscalls = [
        "ptrace",
        "mount",
        "umount2",
        "pivot_root",
        "chroot",
        "reboot",
        "kexec_load",
        "kexec_file_load",
        "init_module",
        "finit_module",
        "delete_module",
        "bpf",
        "userfaultfd",
        "acct",
        "swapon",
        "swapoff",
    ]

    for name in blocked_syscalls:
        try:
            flt.add_rule(seccomp.ERRNO(seccomp.errno.EPERM), name)
        except OSError:
            # Syscall may not exist on this CPU architecture
            pass

    buf = io.BytesIO()
    flt.export_bpf(buf)
    return buf.getvalue()