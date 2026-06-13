# sbx — Custom Sandbox Templates

[![Continuous Integration](https://github.com/thenickfish/docker-ai-sbx/actions/workflows/ci.yml/badge.svg)](https://github.com/thenickfish/docker-ai-sbx/actions/workflows/ci.yml)

Custom Docker sandbox templates for AI coding agents.

## Shared skills

Both images include:

- **[rtk](https://github.com/rtk-ai/rtk)** — token-optimized CLI proxy

## Claude Code

Extends `docker/sandbox-templates:claude-code` with rtk and:

- **[caveman](https://github.com/JuliusBrussee/caveman)** — ultra-compressed communication skill for Claude

### Usage

```bash
sbx run claude --template ghcr.io/thenickfish/docker-ai-sbx-claude:latest --kit ghcr.io/thenickfish/docker-ai-sbx-claude-kit:latest
```

#### Zsh alias

Add this function to your `~/.zshrc` to use this sandbox automatically whenever you run `claude`. It creates a new sandbox with the custom template and kit on first run, and re-attaches to the existing one on subsequent runs:

```zsh
claude() {
  local tmp=$(mktemp)
  sbx run claude --template ghcr.io/thenickfish/docker-ai-sbx-claude:latest --kit ghcr.io/thenickfish/docker-ai-sbx-claude-kit:latest 2>"$tmp" || {
    if grep -q "already exists" "$tmp"; then
      sbx run claude
    else
      cat "$tmp" >&2
    fi
  }
  rm -f "$tmp"
}
```

Then reload your shell:

```bash
source ~/.zshrc
```

## Pi

Extends `docker/sandbox-templates:shell` with rtk and [Pi](https://pi.dev) — a minimal, extensible agent harness supporting 15+ LLM providers. Pi launches automatically in interactive shells.

### Usage

```bash
sbx run shell --template ghcr.io/thenickfish/docker-ai-sbx-pi:latest --kit ghcr.io/thenickfish/docker-ai-sbx-pi-kit:latest
```

#### Zsh alias

```zsh
pi() {
  local tmp=$(mktemp)
  sbx run shell --template ghcr.io/thenickfish/docker-ai-sbx-pi:latest --kit ghcr.io/thenickfish/docker-ai-sbx-pi-kit:latest 2>"$tmp" || {
    if grep -q "already exists" "$tmp"; then
      sbx run shell
    else
      cat "$tmp" >&2
    fi
  }
  rm -f "$tmp"
}
```

## Development

### Build & publish

CI builds and publishes both images on every push to `main`. To publish manually:

```bash
# Both images (uses docker-bake.hcl)
docker buildx bake --push

# Kits
sbx kit push ./claude ghcr.io/thenickfish/docker-ai-sbx-claude-kit:latest
sbx kit push ./pi ghcr.io/thenickfish/docker-ai-sbx-pi-kit:latest

```

### Local run (without publishing)

```bash
# Claude
docker buildx bake claude-local --load && docker image save sbx-claude:latest -o sbx-claude.tar && sbx template load sbx-claude.tar && sbx run claude --template sbx-claude:latest --kit ./claude

# Pi
docker buildx bake pi-local --load && docker image save sbx-pi:latest -o sbx-pi.tar && sbx template load sbx-pi.tar && sbx run shell --template sbx-pi:latest --kit ./pi

# Remove previous sandboxes if needed
sbx rm claude-sbx
sbx rm shell-sbx
```
