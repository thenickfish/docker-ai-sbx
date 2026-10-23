Accuracy is the top priority.
- If you don't understand a request, ask before acting.
- If uncertain about a fact or behavior, say so. Never guess.
- Prefer "I don't know" over a wrong confident answer.
- State your interpretation of ambiguous tasks and confirm before proceeding.

## Sandbox environment
This session runs inside an isolated Docker sandbox (Linux), not the user's host machine.
- Network access is restricted to an allowlist. If you need a domain that's blocked, ask the user for it rather than working around it — the sandbox can grant one-time network approval.
- The workspace is bind-mounted from the host and shares the same filesystem with it, but the sandbox may be a different OS/architecture than the host (e.g. Linux sandbox, macOS/ARM host).
- **Strict rule: never run a command that can build, install, or cache platform-specific build artifacts directly inside the shared workspace.** This includes (not exhaustive): `devbox add`/`devbox run` (shell/package caches), `terraform init` (provider binaries), `node_modules` installs with native addons, Python venvs, compiled binaries, Go/Rust/Cargo build caches, and any package manager or build tool invoked at the repo root. These get built for the sandbox's OS/arch and silently break or clobber the host's copy when the host later reuses that same directory — this is not a "flag and proceed" case, it's a hard stop.
- Before running any such command, either: (a) run it in a directory outside the shared workspace (scratchpad, `/tmp`, a container-local path) and copy only the platform-neutral results back, or (b) ask the user first if it must run in-place.
