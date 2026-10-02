# https://docs.docker.com/ai/sandboxes/customize/templates/#build-a-custom-template
FROM docker/sandbox-templates:shell@sha256:bd90847e98720dde718fe95b24bd4c7d9d4de41966339eb8bf3ab2bb683259e5

USER root

# renovate: datasource=node depName=node tracking=single
ARG NODE_VERSION="24.21.0"
ARG TARGETARCH

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates git fd-find jq ripgrep gnupg \
    && ln -s /usr/bin/fdfind /usr/local/bin/fd \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN ARCH=$(echo "$TARGETARCH" | sed 's/amd64/x64/') \
    && FILENAME="node-v${NODE_VERSION}-linux-${ARCH}.tar.gz" \
    && curl -fsSL "https://nodejs.org/dist/v${NODE_VERSION}/${FILENAME}" -o "/tmp/${FILENAME}" \
    && curl -fsSL "https://nodejs.org/dist/v${NODE_VERSION}/SHASUMS256.txt" \
        | grep "$FILENAME" | (cd /tmp && sha256sum -c) \
    && tar -xzf "/tmp/${FILENAME}" -C /usr/local --strip-components=1 \
    && rm "/tmp/${FILENAME}"

USER agent
ENV PATH="/home/agent/.local/bin:${PATH}"

ARG RTK_VERSION
ARG RTK_COMMIT
ARG CAVEMAN_VERSION
ARG CAVEMAN_COMMIT

RUN git clone --depth 1 --branch "${RTK_VERSION}" https://github.com/rtk-ai/rtk /tmp/rtk \
    && test "$(git -C /tmp/rtk rev-parse HEAD)" = "${RTK_COMMIT}" \
    && RTK_VERSION=${RTK_VERSION} sh /tmp/rtk/install.sh \
    && rm -rf /tmp/rtk \
    && rtk init -g --agent pi

RUN git clone --depth 1 --branch "${CAVEMAN_VERSION}" https://github.com/JuliusBrussee/caveman /tmp/caveman \
    && test "$(git -C /tmp/caveman rev-parse HEAD)" = "${CAVEMAN_COMMIT}" \
    && mkdir -p ~/.agents/skills \
    && cp -r /tmp/caveman/skills/* ~/.agents/skills/ \
    && rm -rf /tmp/caveman

# install devbox
ARG DEVBOX_VERSION
RUN FILENAME="devbox_${DEVBOX_VERSION}_linux_${TARGETARCH}.tar.gz" \
    && curl -fsSL "https://github.com/jetify-com/devbox/releases/download/${DEVBOX_VERSION}/${FILENAME}" -o "/tmp/${FILENAME}" \
    && curl -fsSL "https://github.com/jetify-com/devbox/releases/download/${DEVBOX_VERSION}/checksums.txt" \
        | grep "$FILENAME" | (cd /tmp && sha256sum -c) \
    && tar -xzf "/tmp/${FILENAME}" -C ~/.local/bin devbox \
    && rm "/tmp/${FILENAME}"

# install op CLI (1Password) — unauthenticated; available for command exploration
ARG OP_VERSION
RUN FILENAME="op_linux_${TARGETARCH}_v${OP_VERSION}.zip" \
    && curl -fsSL "https://cache.agilebits.com/dist/1P/op2/pkg/v${OP_VERSION}/${FILENAME}" -o "/tmp/${FILENAME}" \
    && curl -fsSL "https://raw.githubusercontent.com/1Password/install-cli-action/main/src/op-cli-installer/github-action/cli-installer/linux-signing-key.asc" | gpg --import \
    && mkdir /tmp/op_extract \
    && python3 -c "import zipfile; z=zipfile.ZipFile('/tmp/${FILENAME}'); z.extract('op', '/tmp/op_extract'); z.extract('op.sig', '/tmp/op_extract')" \
    && gpg --verify /tmp/op_extract/op.sig /tmp/op_extract/op \
    && mv /tmp/op_extract/op ~/.local/bin/op \
    && chmod +x ~/.local/bin/op \
    && rm -rf "/tmp/${FILENAME}" /tmp/op_extract

COPY --chown=agent:agent package.json /home/agent/pi-pkg/package.json
COPY --chown=agent:agent settings.json /home/agent/.pi/agent/settings.json
COPY --chown=agent:agent nebula.json /home/agent/.pi/agent/themes/nebula.json
COPY --chown=agent:agent AGENTS.md /home/agent/.pi/agent/AGENTS.md
COPY --chown=agent:agent APPEND_SYSTEM.md /home/agent/.pi/agent/APPEND_SYSTEM.md

RUN mkdir -p "$HOME/.npm-global" \
    && npm config set prefix "$HOME/.npm-global" \
    && npm config set ignore-scripts true \
    && printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc \
    && PI_VERSION=$(node -p "require('/home/agent/pi-pkg/package.json').devDependencies['@earendil-works/pi-coding-agent']") \
    && npm install -g "@earendil-works/pi-coding-agent@${PI_VERSION}" \
    && npm install --prefix /home/agent/pi-pkg --omit=dev \
    && mkdir -p "$HOME/.pi/agent/extensions" \
    && cp -r /home/agent/pi-pkg/node_modules/@ollama "$HOME/.pi/agent/extensions/" \
    && cp -r /home/agent/pi-pkg/node_modules/pi-ollama "$HOME/.pi/agent/extensions/" \
    && cp -r /home/agent/pi-pkg/node_modules/pi-powerline-footer "$HOME/.pi/agent/extensions/" \
    && rm -rf /home/agent/pi-pkg

ENV OLLAMA_HOST=host.docker.internal:11434
ENV CAVEMAN_MODE=full

RUN printf '\nif [[ $- == *i* ]] && command -v pi &> /dev/null; then\n    exec pi\nfi\n' >> ~/.bashrc
