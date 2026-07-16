# Pi Sandbox

Extends `docker/sandbox-templates:shell` with:

- **[rtk](https://github.com/rtk-ai/rtk)** — token-optimized CLI proxy
- **[caveman](https://github.com/JuliusBrussee/caveman)** — ultra-compressed communication skill, auto-activates on session start
- **[Pi](https://pi.dev)** — minimal, extensible agent harness supporting 15+ LLM providers, launches automatically
- **[pi-ollama](https://github.com/CaptCanadaMan/pi-ollama)** — native Ollama provider, pre-installed
- **[devbox](https://github.com/jetify-com/devbox)** — reproducible dev environments
- **[renovate](https://github.com/renovatebot/renovate)** — automated dependency updates
- **[docker](https://www.docker.com)** — Docker CLI + daemon binaries

## Usage

```bash
sbx run shell --template ghcr.io/thenickfish/docker-ai-sbx-pi:latest --kit ghcr.io/thenickfish/docker-ai-sbx-pi-kit:latest
```

### Zsh alias

Add to `~/.zshrc` to auto-create on first run and re-attach on subsequent runs:

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

## Ollama (local LLM)

The sandbox connects to Ollama running on your host machine.

1. Start Ollama bound to all interfaces, get a model installed:
2. Inside Pi, switch models with `/model`. If Ollama wasn't running at startup, run `/ollama-refresh` first.

> `OLLAMA_HOST` is pre-set to `host.docker.internal:11434`. Network access is allowed via the kit.

## Local build & run

```bash
docker buildx bake pi --load && docker image save ghcr.io/thenickfish/docker-ai-sbx-pi:latest -o sbx-pi.tar && sbx template load sbx-pi.tar && sbx run shell --template ghcr.io/thenickfish/docker-ai-sbx-pi:latest --kit ./pi
```

Remove sandbox: `sbx rm shell-sbx`
