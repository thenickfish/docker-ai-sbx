On session start: activate /caveman full immediately

## Sandbox constraints

### Platform
This session runs inside an isolated Docker sandbox (Linux), not the user's host machine. The workspace is bind-mounted from the host and shares the same filesystem with it, but the sandbox may be a different OS/architecture (e.g. Linux sandbox, macOS/ARM host).

**Strict rule: never run a command that can build, install, or cache platform-specific build artifacts directly inside the shared workspace.** This includes (not exhaustive): `devbox add`/`devbox run` (shell/package caches), `terraform init` (provider binaries), `node_modules` installs with native addons, Python venvs, compiled binaries, Go/Rust/Cargo build caches, and any package manager or build tool invoked at the repo root. These get built for the sandbox's OS/arch and silently break or clobber the host's copy when the host later reuses that same directory — this is not a "flag and proceed" case, it's a hard stop.

Before running any such command, either: (a) run it in a directory outside the shared workspace (scratchpad, `/tmp`, a container-local path) and copy only the platform-neutral results back, or (b) ask the user first if it must run in-place.

### Network access
Outbound network is restricted to an allowlist. Blocked requests return HTTP 403.

**When a request is blocked: stop immediately. Do not retry, probe alternative URLs, or attempt workarounds.**

Tell the user exactly which domain is blocked and ask them to run on their host:
```
sbx policy approval ls
sbx policy approval respond <approval-id> --option <option-id>
```
Wait for confirmation before proceeding. The sandbox can grant one-time or persistent approval for any domain.

## Local dev tools

### devbox
Prefer devbox over system package managers (apt, npm -g, pip, brew). Use `devbox add <pkg>` to add packages and `devbox run <script>` for convenience scripts. This keeps deps isolated to the project and avoids polluting the system environment.

Always pin explicit versions: `devbox add pkg@<version>` (e.g. `devbox add node@22.0.0`). Never rely on unversioned `devbox add pkg` — it resolves to latest at install time and breaks reproducibility. Look up the current version first with `devbox search <pkg>`, then pin it.

### 1Password CLI (op)
`op` is installed but there is no authenticated session. `op signin` and any vault/item operations will fail. You can explore available commands with `op --help` or `op <subcommand> --help`.
