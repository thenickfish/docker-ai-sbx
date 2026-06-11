# sbx — Custom Claude Code Sandbox Template

A custom Docker image for Claude Code sandboxes, extending the official `docker/sandbox-templates:claude-code` base with additional tooling.

## What's included

- **[rtk](https://github.com/rtk-ai/rtk)** — installed globally with `--hook-only --auto-patch`
- **[caveman](https://github.com/JuliusBrussee/caveman)** — added as a Claude Code skill via `npx skills add`

## Usage

Run using published artifacts:

```bash
sbx run claude --template ghcr.io/thenickfish/docker-ai-sbx:latest --kit ghcr.io/thenickfish/docker-ai-sbx-kit:latest
```

## Development

### Build & publish

CI builds and publishes on every push to `main`. To publish manually:

```bash
# Build
docker build -t ghcr.io/thenickfish/docker-ai-sbx:latest .

# Push the image
docker push ghcr.io/thenickfish/docker-ai-sbx:latest

# Push the kit
sbx kit push . ghcr.io/thenickfish/docker-ai-sbx-kit:latest

# All-in-one
docker build -t ghcr.io/thenickfish/docker-ai-sbx:latest . && docker push ghcr.io/thenickfish/docker-ai-sbx:latest && sbx kit push . ghcr.io/thenickfish/docker-ai-sbx-kit:latest
```

### Local run (without publishing)

The `spec.yaml` kit writes `settings.json` (rtk hooks) and `CLAUDE.md` at sandbox startup,
after the sandbox initialises — ensuring they aren't overwritten by default sandbox init.

```bash
# Build, export, load, and run
docker build -t sbx:latest . && docker image save sbx:latest -o sbx.tar && sbx template load sbx.tar && sbx run claude --template sbx:latest --kit .

# Remove previous sandbox first if needed
sbx rm claude-sbx
```
