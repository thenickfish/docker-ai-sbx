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
- **Kit** — the mixin overlay: `spec.yaml` + any config assets (no image build). Pushed separately via `sbx kit push`. Runs at sandbox start.

When `sbx run` is called: template image is pulled, then the kit's `startup` commands execute on top.

## Critical: spec.yaml is source of truth for sandbox config

`spec.yaml` startup commands overwrite `/home/agent/.claude/settings.json` and `/home/agent/.claude/CLAUDE.md` **on every sandbox start**. Never edit those files directly inside a running sandbox — changes are lost on restart.

**To change sandbox behavior: edit `spec.yaml`**, not the sandbox files.

### What the claude startup command writes

- `settings.json` — rtk `PreToolUse` hook, `skipDangerousModePermissionPrompt: true`, caveman plugin enabled
- `CLAUDE.md` — `On session start: activate /caveman full immediately`

## Pi agent config

Pi is a separate coding agent (not Claude Code). It auto-starts in the shell sandbox when an interactive terminal opens.

Key files in `pi/`:
- `spec.yaml` — network policy (allows `localhost` for Ollama), no startup commands needed
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
  sbx kit push ./claude ghcr.io/thenickfish/docker-ai-sbx-claude-kit:latest && \
  sbx kit push ./pi    ghcr.io/thenickfish/docker-ai-sbx-pi-kit:latest

# Run from published artifacts (CI pushes on merge to main)
sbx run claude --template ghcr.io/thenickfish/docker-ai-sbx-claude:latest --kit ghcr.io/thenickfish/docker-ai-sbx-claude-kit:latest
sbx run shell  --template ghcr.io/thenickfish/docker-ai-sbx-pi:latest    --kit ghcr.io/thenickfish/docker-ai-sbx-pi-kit:latest

# Local build (no push)
docker buildx bake claude-local --load && docker image save sbx-claude:latest -o sbx-claude.tar && sbx template load sbx-claude.tar && sbx run claude --template sbx-claude:latest --kit ./claude
docker buildx bake pi-local     --load && docker image save sbx-pi:latest    -o sbx-pi.tar    && sbx template load sbx-pi.tar    && sbx run shell  --template sbx-pi:latest    --kit ./pi

# Cleanup
sbx rm claude-sbx
sbx rm shell-sbx
```

## Testing

`claude/test.py` runs inside the Docker build. CI uses `claude-test` (multi-platform). Run locally with the single-platform target:

```bash
docker buildx bake claude-test-local
```

`test.py` asserts: rtk installed, devbox installed, caveman skills/plugin present, spec.yaml startup produces correct `settings.json` and `CLAUDE.md`.

> This sandbox has no Docker daemon — tests must be run on the host.

## rtk usage

```bash
rtk gain          # token savings analytics
rtk discover      # find missed rtk opportunities in history
rtk read <file>   # token-optimized file read (prefer over cat)
```

## Devbox

```bash
devbox run renovate-dry-run   # test Renovate config locally (LOG_LEVEL=debug, outputs to /tmp/renovate-dry-run.log)
```
