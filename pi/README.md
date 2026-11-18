# Pi Sandbox

Extends `docker/sandbox-templates:shell` with:

- **[rtk](https://github.com/rtk-ai/rtk)** — token-optimized CLI proxy
- **[caveman](https://github.com/JuliusBrussee/caveman)** — ultra-compressed communication skill, auto-activates on session start
- **[Pi](https://pi.dev)** — minimal, extensible agent harness supporting 15+ LLM providers, launches automatically
- **[pi-ollama](https://github.com/CaptCanadaMan/pi-ollama)** — native Ollama provider, pre-installed

## Usage

```bash
sbx run shell --template ghcr.io/thenickfish/docker-ai-sbx-pi:latest --kit ghcr.io/thenickfish/docker-ai-sbx-pi-kit:latest
```

### Zsh alias

Add to `~/.zshrc`. Runs Pi in a sandbox for the current directory (`shell-<dir>`) using the latest image and kit. If that sandbox already exists you are asked to attach or delete and re-create it (re-creating is how you pick up new image/kit versions). Extra arguments go to Pi.

```zsh
pi() {
  local name="shell-${PWD:t}"
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

  sbx run shell --name "$name" \
    --template ghcr.io/thenickfish/docker-ai-sbx-pi:latest \
    --kit ghcr.io/thenickfish/docker-ai-sbx-pi-kit:latest "${args[@]}"
}
```

## Ollama (local LLM)

The sandbox connects to Ollama running on your host machine.

1. Start Ollama bound to all interfaces, get a model installed:
2. Inside Pi, switch models with `/model`. If Ollama wasn't running at startup, run `/ollama-refresh` first.

> `OLLAMA_HOST` is pre-set to `host.docker.internal:11434`. Network access is allowed via the kit.

## Local build & run

```bash
docker buildx bake pi-local --load && docker image save sbx-pi:latest -o sbx-pi.tar && sbx template load sbx-pi.tar && sbx run shell --template sbx-pi:latest --kit ./pi-kit
```

Remove sandbox: `sbx rm shell-sbx`
