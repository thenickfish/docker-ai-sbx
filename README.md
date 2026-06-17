# sbx — Custom Sandbox Templates

[![Continuous Integration](https://github.com/thenickfish/docker-ai-sbx/actions/workflows/ci.yml/badge.svg)](https://github.com/thenickfish/docker-ai-sbx/actions/workflows/ci.yml)

Custom Docker sandbox templates for AI coding agents. Both images include **[rtk](https://github.com/rtk-ai/rtk)**, **[caveman](https://github.com/JuliusBrussee/caveman)**, and **[devbox](https://github.com/jetify-com/devbox)**.

## Templates

| Template | Agent | Run command |
|----------|-------|-------------|
| [Claude Code](claude/README.md) | Claude Code CLI | `sbx run claude --template ghcr.io/thenickfish/docker-ai-sbx-claude:latest --kit ghcr.io/thenickfish/docker-ai-sbx-claude-kit:latest` |
| [Pi](pi/README.md) | [Pi](https://pi.dev) — 15+ LLM providers, Ollama support | `sbx run shell --template ghcr.io/thenickfish/docker-ai-sbx-pi:latest --kit ghcr.io/thenickfish/docker-ai-sbx-pi-kit:latest` |

## Development

CI builds and publishes both images on every push to `main`. To publish manually:

```bash
# Images
docker buildx bake --push

# Kits
sbx kit push ./claude ghcr.io/thenickfish/docker-ai-sbx-claude-kit:latest
sbx kit push ./pi ghcr.io/thenickfish/docker-ai-sbx-pi-kit:latest
```
