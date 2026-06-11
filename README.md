# sbx — Custom Claude Code Sandbox Template

A custom Docker image for Claude Code sandboxes, extending the official `docker/sandbox-templates:claude-code` base with additional tooling.

## What's included

- **[rtk](https://github.com/rtk-ai/rtk)** — installed globally with `--hook-only --auto-patch`
- **[caveman](https://github.com/JuliusBrussee/caveman)** — added as a Claude Code skill via `npx skills add`

## Usage

### Build

```bash
docker build -t sbx:latest .
```

### Export, load, and run using the kit

The `spec.yaml` kit writes `settings.json` (rtk hooks) and `CLAUDE.md` at sandbox startup,
after the sandbox initialises — ensuring they aren't overwritten by default sandbox init.

```bash
# Export the image to a tar archive
docker image save sbx:latest -o sbx.tar

# Load it as a sandbox template
sbx template load sbx.tar

# Run a Claude Code session using the kit (spec.yaml in current directory)
sbx run claude --template sbx:latest --kit .

# remove previous sbx
sbx rm claude-sbx

# all-in-one
docker build -t sbx:latest . && docker image save sbx:latest -o sbx.tar && sbx template load sbx.tar && sbx run claude --template sbx:latest --kit .
```
