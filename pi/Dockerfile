# https://docs.docker.com/ai/sandboxes/customize/templates/#build-a-custom-template
FROM docker/sandbox-templates:shell@sha256:bc721fe1cfddfb234bec0f11c068a38e049cf517e0e278f932b9e241088362f0

USER root

# renovate: datasource=node depName=node tracking=single
ARG NODE_VERSION="24.16.0"
ARG TARGETARCH

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates git fd-find \
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
RUN echo "ignore-scripts=true" >> /home/agent/.npmrc
ENV PATH="/home/agent/.local/bin:${PATH}"

ARG RTK_VERSION
ARG RTK_COMMIT
ARG CAVEMAN_VERSION
ARG CAVEMAN_COMMIT

# install rtk
RUN git clone --depth 1 --branch "${RTK_VERSION}" https://github.com/rtk-ai/rtk /tmp/rtk \
    && test "$(git -C /tmp/rtk rev-parse HEAD)" = "${RTK_COMMIT}" \
    && RTK_VERSION=${RTK_VERSION} sh /tmp/rtk/install.sh \
    && rm -rf /tmp/rtk \
    && rtk init -g --agent pi

# install caveman skills
RUN git clone --depth 1 --branch "${CAVEMAN_VERSION}" https://github.com/JuliusBrussee/caveman /tmp/caveman \
    && test "$(git -C /tmp/caveman rev-parse HEAD)" = "${CAVEMAN_COMMIT}" \
    && mkdir -p ~/.agents/skills \
    && cp -r /tmp/caveman/skills/* ~/.agents/skills/ \
    && rm -rf /tmp/caveman

# renovate: datasource=npm depName=@earendil-works/pi-coding-agent tracking=single
ARG PI_VERSION="0.79.1"
# renovate: datasource=npm depName=pi-ollama tracking=single
ARG PI_OLLAMA_VERSION="0.1.5"

RUN mkdir -p "$HOME/.npm-global" \
    && npm config set prefix "$HOME/.npm-global" \
    && npm config set ignore-scripts true \
    && printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc \
    && npm install -g "@earendil-works/pi-coding-agent@${PI_VERSION}"

# install pi-ollama extension into Pi's global extensions directory
RUN mkdir -p "$HOME/.pi/agent/extensions/pi-ollama" \
    && npm pack "pi-ollama@${PI_OLLAMA_VERSION}" --pack-destination /tmp \
    && tar -xzf "/tmp/pi-ollama-${PI_OLLAMA_VERSION}.tgz" -C "$HOME/.pi/agent/extensions/pi-ollama" --strip-components=1 \
    && rm "/tmp/pi-ollama-${PI_OLLAMA_VERSION}.tgz"

ENV OLLAMA_HOST=host.docker.internal:11434

RUN mkdir -p "$HOME/.pi/agent" \
    && printf 'On session start: activate /caveman full immediately\n' > "$HOME/.pi/agent/AGENTS.md"

RUN printf '\n# Activate caveman by default\nexport CAVEMAN_MODE=full\n\nif [[ $- == *i* ]] && command -v pi &> /dev/null; then\n    exec pi\nfi\n' >> ~/.bashrc
