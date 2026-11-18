# sbx — Claude Code Sandbox

Two Docker sandbox images with similar tools (rtk and caveman) pre-installed:
- **claude** — Claude Code agent (`docker/sandbox-templates:claude-code` base)
- **pi** — Pi coding agent (`docker/sandbox-templates:shell` base, Node 24, Pi CLI auto-starts)

## Adding Tools

When adding new tools, do the following:
- ensure the upgrade is managed by Renovate - prefer following the pattern that uses docker-bake.hcl
- update CLAUDE.md and README.md to reflect the new tool
- validate that the container builds still succeed after the change
- if there are tests, update them to test the new tool

## Kit vs Template

- **Template** — the Docker image (built via `docker-bake.hcl`, pushed to GHCR)
- **Kit** — the v3 mixin overlay: `claude-kit/spec.yaml`, `pi-kit/spec.yaml` (declaration only, no image build). Pushed separately via `docker buildx build ./<kit> -f ./<kit>/spec.yaml --push -t <ref>` (the v3 build frontend; `sbx kit push` only handles v1/v2). Runs at sandbox start.

When `sbx run` is called: template image is pulled, then the kit's lifecycle hooks (install once, startup every boot) and agent-context are composed on top of the v3 workload.

## Critical: the kit specs are source of truth for sandbox config

Both kits use `schemaVersion: "3"` (`kind: mixin`, `# syntax=docker/sandbox-kit:3`). Spec: https://github.com/docker/sandbox-kit-spec (docs/spec/SPEC-v3.md). The built-in `claude` and `shell` agents are v3 workloads, and v1/v2 and v3 kits cannot be mixed, so the kits must stay v3. Never edit kit-managed files directly inside a running sandbox, they are overwritten on recreation.

**To change sandbox behavior: edit `claude-kit/spec.yaml` or `pi-kit/spec.yaml`**, not the sandbox files.

Kit identity in v3 is the directory basename (there is no `name` field), so the kit dirs must not collide with a workload name. That is why they are `claude-kit/` and `pi-kit/`, not `claude/` and `pi/`.

Both kits are declaration-only (no Dockerfile): all tools (rtk, caveman, nix, devbox, op, statusline, pi) live in the template images, built from `claude/Dockerfile` and `pi/Dockerfile`, and used via `--template`. Do not drop `--template`.

### What the claude kit declares (`claude-kit/spec.yaml`)

- `lifecycle@1` `install` (root, once at creation): appends `unset GH_TOKEN` to `/etc/sandbox-persistent.sh`
- `lifecycle@1` `startup` (agent, every start):
  - deep-merges the kit settings JSON (rtk `PreToolUse` hook, `skipDangerousModePermissionPrompt`, caveman plugin, `statusLine`) onto `~/.claude/settings.json` via `jq`. The JSON is a heredoc inside the startup command. Needed because Claude Code rewrites `settings.json` and drops unknown keys.
  - appends an `@import` of `~/.claude/kits-agent-context/claude-kit.md` to `~/.claude/CLAUDE.md`. v3 delivers kit guidance as a lazy index entry, so without the import the "activate /caveman full" line never fires at session start.
- `agent-context@2`: sandbox guidance (caveman, network policy, devbox, op). Inline `content`, no `directory` (tool mixin).

Validate: `SBX_KIT_BUILDER=host sbx kit validate ./claude-kit` (needs Docker running), or `SBX_KIT_BUILDER=sandbox`.

## Pi agent config

Pi is a separate coding agent (not Claude Code). It auto-starts in the shell sandbox when an interactive terminal opens.

Key files in `pi/`:
- `pi-kit/spec.yaml` (kit, outside `pi/`) — network policy (allows `localhost` for Ollama), no startup commands needed
- `AGENTS.md` — Pi's equivalent of CLAUDE.md (caveman activation)
- `APPEND_SYSTEM.md` — appended to Pi's system prompt (accuracy/behavior instructions)
- `nebula.json` — Pi color theme (Catppuccin Mocha palette)
- `package.json` — Pi version and extensions (pi-ollama, pi-powerline-footer)
- `settings.json` — Pi agent settings

Pi + Ollama: start Ollama on host with `OLLAMA_HOST=0.0.0.0 ollama serve`, then switch models with `/model` inside Pi.

## Renovate version annotation convention

Renovate uses regex custom managers. Version variables **must** have the exact comment annotation on the line immediately above them — no blank lines between comment and variable.

### docker-bake.hcl — version + commit pair (git-cloned tools)

```hcl
# renovate: datasource=github-releases depName=rtk-ai/rtk
variable "RTK_VERSION" { default = "v0.42.3" }
variable "RTK_COMMIT"  { default = "de78d70aee86fe6b7b5c2462820a1b6c250d425b" }
```

Both variables must stay adjacent. Renovate updates `RTK_VERSION` (currentValue) and `RTK_COMMIT` (currentDigest) together.

### docker-bake.hcl — single version (binary releases, no commit hash)

Use `tracking=single` when there's no commit to verify against:

```hcl
# renovate: datasource=github-releases depName=jetify-com/devbox tracking=single
variable "DEVBOX_VERSION" { default = "0.13.7" }
```

### Dockerfile — single ARG tracking

```dockerfile
# renovate: datasource=node depName=node tracking=single
ARG NODE_VERSION="24.16.0"
```

### ci.yml — git-refs with currentValue + currentDigest

```yaml
# renovate: datasource=git-refs depName=https://github.com/docker/docker-install currentValue=master
git -C /tmp/docker-install checkout 153e238e1d876160ea4a2a1844ca7f2983bbdd5e
```

## GitHub Actions: always pin to commit SHA

Never use mutable tags (`@v4`). Pin to the full SHA of the latest release:

```yaml
# Good
- uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6.0.3

# Bad
- uses: actions/checkout@v4
```

Lookup: `git ls-remote https://github.com/actions/checkout` or the releases page. Add the version tag as a comment.

## Build & run commands

```bash
# Build & push both images + kits (requires GHCR login)
docker buildx bake --push && \
  docker buildx build ./claude-kit -f ./claude-kit/spec.yaml --platform linux/amd64,linux/arm64 --push -t ghcr.io/thenickfish/docker-ai-sbx-claude-kit:latest && \
  docker buildx build ./pi-kit -f ./pi-kit/spec.yaml --platform linux/amd64,linux/arm64 --push -t ghcr.io/thenickfish/docker-ai-sbx-pi-kit:latest

# Run from published artifacts (CI pushes on merge to main)
sbx run claude --template ghcr.io/thenickfish/docker-ai-sbx-claude:latest --kit ghcr.io/thenickfish/docker-ai-sbx-claude-kit:latest
sbx run shell  --template ghcr.io/thenickfish/docker-ai-sbx-pi:latest    --kit ghcr.io/thenickfish/docker-ai-sbx-pi-kit:latest

# Local build (no push)
docker buildx bake claude-local --load && docker image save sbx-claude:latest -o sbx-claude.tar && sbx template load sbx-claude.tar && sbx run claude --template sbx-claude:latest --kit ./claude-kit
docker buildx bake pi-local     --load && docker image save sbx-pi:latest    -o sbx-pi.tar    && sbx template load sbx-pi.tar    && sbx run shell  --template sbx-pi:latest    --kit ./pi-kit

# Cleanup
sbx rm claude-sbx
sbx rm shell-sbx
```

## Testing

`claude/test.py` runs inside the Docker build. CI uses `claude-test` (multi-platform). Run locally with the single-platform target:

```bash
docker buildx bake claude-test-local
```

`test.py` asserts: rtk installed, devbox installed, caveman skills/plugin present, `claude-kit/spec.yaml` startup (passed to the build as the `kit` named context) produces correct `settings.json` and the `CLAUDE.md` import.

> This sandbox has no Docker daemon — tests must be run on the host.

## GitHub API access (gh CLI)

The proxy handles git HTTPS credentials automatically. For `gh` CLI API calls, a separate one-time setup is required on the host.

The install hook in `claude-kit/spec.yaml` unsets the proxy's `GH_TOKEN` sentinel so `gh` falls back to `GITHUB_TOKEN`. The proxy then substitutes the real token on outbound `api.github.com` requests.

**One-time host setup:**

```bash
# Create a fine-grained PAT at https://github.com/settings/personal-access-tokens/new
# Scopes: Contents (read), Metadata (read), Pull requests (read), Issues (read)
sbx secret set-custom \
  --host api.github.com \
  --env GITHUB_TOKEN \
  --placeholder "github_pat_{rand}" \
  --value "<your-readonly-PAT>"
```

Git push/fetch continue to work via the built-in `github` service secret.

## rtk usage

```bash
rtk gain          # token savings analytics
rtk discover      # find missed rtk opportunities in history
rtk read <file>   # token-optimized file read (prefer over cat)
```

## Devbox

```bash
devbox run renovate-dry-run   # test Renovate config locally (LOG_LEVEL=debug, outputs to /tmp/renovate-dry-run.log)
devbox run run-claude-local   # build + load the claude template and run a sandbox against the local ./claude-kit kit (no registry/kit push)
```
