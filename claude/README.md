# Claude Code Sandbox

Extends `docker/sandbox-templates:claude-code` with:

- **[rtk](https://github.com/rtk-ai/rtk)** — token-optimized CLI proxy
- **[caveman](https://github.com/JuliusBrussee/caveman)** — ultra-compressed communication skill, auto-activates on session start
- **[devbox](https://github.com/jetify-com/devbox)** — reproducible dev environments
- **[renovate](https://github.com/renovatebot/renovate)** — automated dependency updates
- **[docker](https://www.docker.com)** — Docker CLI + daemon binaries

## Usage

```bash
sbx run claude --template ghcr.io/thenickfish/docker-ai-sbx-claude:latest --kit ghcr.io/thenickfish/docker-ai-sbx-claude-kit:latest
```

### Zsh alias

Add to `~/.zshrc` to auto-create on first run and re-attach on subsequent runs:

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

## Local build & run

```bash
docker buildx bake claude --load && docker image save ghcr.io/thenickfish/docker-ai-sbx-claude:latest -o sbx-claude.tar && sbx template load sbx-claude.tar && sbx run claude --template ghcr.io/thenickfish/docker-ai-sbx-claude:latest --kit ./claude
```

Remove sandbox: `sbx rm claude-sbx`
