# Claude Code Sandbox

Extends `docker/sandbox-templates:claude-code` with:

- **[rtk](https://github.com/rtk-ai/rtk)** — token-optimized CLI proxy
- **[caveman](https://github.com/JuliusBrussee/caveman)** — ultra-compressed communication skill, auto-activates on session start

## Usage

```bash
sbx run claude --template ghcr.io/thenickfish/docker-ai-sbx-claude:latest --kit ghcr.io/thenickfish/docker-ai-sbx-claude-kit:latest
```

### Zsh alias

Add to `~/.zshrc`. Runs Claude in a sandbox for the current directory (`claude-<dir>`) using the latest image and kit. If that sandbox already exists you are asked to attach or delete and re-create it (re-creating is how you pick up new image/kit versions). Extra arguments go to Claude, e.g. `claude --resume`.

```zsh
claude() {
  local name="claude-${PWD:t}"
  name=${name//[^A-Za-z0-9.-]/-}
  local -a args=()
  (( $# )) && args=(-- "$@")

  if sbx ls 2>/dev/null | awk -v n="$name" 'NR > 1 && $1 == n { f = 1 } END { exit !f }'; then
    local choice
    read -k 1 "choice?Sandbox '$name' exists. [a]ttach, [r]e-create, [c]ancel? "
    echo
    case $choice in
      a|A) sbx run --name "$name" "${args[@]}"; return ;;
      r|R) sbx rm --force "$name" || return ;;
      *) return 0 ;;
    esac
  fi

  sbx run claude --name "$name" \
    --template ghcr.io/thenickfish/docker-ai-sbx-claude:latest \
    --kit ghcr.io/thenickfish/docker-ai-sbx-claude-kit:latest "${args[@]}"
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

Neither command pushes images or the kit to the registry — both run entirely against local artifacts.

```bash
devbox run run-claude-local   # build + load the template, run a sandbox against the local ./claude-kit kit
```

Equivalent raw command:

```bash
docker buildx bake claude-local --load && docker image save sbx-claude:latest -o sbx-claude.tar && sbx template load sbx-claude.tar && sbx run claude --template sbx-claude:latest --kit ./claude-kit
```

Remove sandbox: `sbx rm claude-sbx`
