# AGENT-SANDBOXES

**Why:** Building this project from the ground up to research and understand sandboxes for AI agents.

## Progression

| Level | Directory                         | Mechanism                                                      | Host OS       |
| :---- | :-------------------------------- | :------------------------------------------------------------- | :------------ |
| **1** | `level_1_basic_subprocess/`       | `subprocess.run` + timeout                                     | macOS / Linux |
| **2** | `level_2_restricted_env_fs/`      | Scrubbed `env` + ephemeral `cwd`                               | macOS / Linux |
| **3** | `level_3_linux_namespaces/`       | `unshare` (`--net`, `--pid`, `--mount-proc`)                   | Linux         |
| **4** | `level_4_bubblewrap_isolation/`   | `bubblewrap` (`--unshare-all`, read-only mounts, `/workspace`) | Linux         |
| **5** | `level_5_airtight_bwrap_seccomp/` | `bwrap` + `seccomp` BPF filter + resource limits               | Linux         |

## Workflow

- paste test payloads from Claude or Gemini web/CLI sessions into `agent_code.py` or `test_attacks.py`.
- Run Levels 1–2 locally on macOS; run Levels 3–5 inside a Linux VM/container (`unshare`, `bubblewrap`, `libseccomp`).
- Document every bypassed attack and mitigated vulnerability in each level's `README.md`.
