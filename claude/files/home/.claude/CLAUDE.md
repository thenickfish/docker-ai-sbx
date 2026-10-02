On session start: activate /caveman full immediately

## Sandbox constraints

### Platform
This session runs inside an isolated Docker sandbox (Linux), not the user's host machine. The workspace is bind-mounted from the host, but the sandbox may be a different OS/architecture (e.g. Linux sandbox, macOS/ARM host). Don't run commands that write platform-specific build artifacts into the shared workspace (`terraform init` providers, `node_modules` with native addons, compiled binaries, venvs) without flagging it first — they'll be built for the sandbox's platform and can silently break when the host later reuses that same directory.

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
