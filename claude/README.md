# Claude Code Sandbox

Extends `docker/sandbox-templates:claude-code` with:

- **[rtk](https://github.com/rtk-ai/rtk)** — token-optimized CLI proxy
- **[caveman](https://github.com/JuliusBrussee/caveman)** — ultra-compressed communication skill, auto-activates on session start

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

## GitHub API access (gh CLI)

The sandbox proxy manages git HTTPS credentials automatically. For `gh` CLI API access (issues, PRs, etc.), set up a readonly fine-grained PAT once on the host:

```bash
# Create a fine-grained PAT at https://github.com/settings/personal-access-tokens/new
# Scopes: Contents (read), Metadata (read), Pull requests (read), Issues (read)
sbx secret set-custom \
  --host api.github.com \
  --env GITHUB_TOKEN \
  --placeholder "github_pat_{rand}" \
  --value "<your-readonly-PAT>"
```

The startup script unsets the proxy's `GH_TOKEN` sentinel so `gh` falls back to `GITHUB_TOKEN`. The proxy then substitutes the real token on outbound requests to `api.github.com`. Git push/fetch continue to work via the built-in `github` service secret.

## Local build & run

```bash
docker buildx bake claude-local --load && docker image save sbx-claude:latest -o sbx-claude.tar && sbx template load sbx-claude.tar && sbx run claude --template sbx-claude:latest --kit ./claude
```

Remove sandbox: `sbx rm claude-sbx`
