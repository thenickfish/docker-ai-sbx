On session start: activate /caveman full immediately

## Behavior

- Recommend the technologies, languages, or frameworks that make sense for the task.
- When dealing with dependencies, prefer pinning to immutable digests, annotate them with renovate regex matcher comments so they can be upgraded.
- Ambiguity: proceed on low-risk decisions, stop and ask before destructive or irreversible actions
- Tests: write for every update, run after every code change
- Explanations: skip prose, show diffs and data
- When designing solutions, be cost-effective. Use free tiers of cloud services, or self-hosting.

## Docker Daemon

`dockerd` is installed but not started. Start it on-demand before any `docker` command or if you find you need a docker socket.

```bash
sudo dockerd --group agent &>/tmp/dockerd.log &
timeout 15 sh -c 'until docker info &>/dev/null 2>&1; do sleep 1; done'
```

## Hard rules

- Never interact with git without being explicitly asked
- Never modify lockfiles directly — run the package manager
- Never truncate or delete data without asking

## Tooling preferences

- [GitHub Actions](https://docs.github.com/en/actions/) for CI/CD
    - write logic in a platform agnostic way where it makes sense.
- [Devbox](https://github.com/jetify-com/devbox) is used to install other dependencies (search via `devbox search`), and add scripts for common tasks.
- [Renovate](https://renovatebot.com/) for package updates, when packages are being added ensure they are compatible. If a project is missing a renovate.json, add it.
- [OpenTofu](https://www.opentofu.org/)/ [Terraform](https://developer.hashicorp.com/terraform/) for infrastructure as code
- [Kubernetes](https://kubernetes.io/) for container orchestration and deployment, for custom solutions use [Kustomize](https://github.com/kubernetes-sigs/kustomize/), and for open source or vended solutions use [Helm](https://helm.sh/)
