# https://docs.docker.com/ai/sandboxes/customize/templates/#build-a-custom-template
FROM docker/sandbox-templates:claude-code@sha256:72570e76fbb20c9bd8b945efea169fe0f2e0696e80d489125e1206d6d409ee91 AS base
USER agent
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
    && rtk init -g --auto-patch

# install caveman
RUN git clone --depth 1 --branch "${CAVEMAN_VERSION}" https://github.com/JuliusBrussee/caveman /tmp/caveman \
    && test "$(git -C /tmp/caveman rev-parse HEAD)" = "${CAVEMAN_COMMIT}" \
    && bash /tmp/caveman/install.sh \
    && mkdir -p ~/.claude/skills \
    && cp -r /tmp/caveman/skills/* ~/.claude/skills/ \
    && rm -rf /tmp/caveman

# install devbox
ARG DEVBOX_VERSION
ARG TARGETARCH
RUN FILENAME="devbox_${DEVBOX_VERSION}_linux_${TARGETARCH}.tar.gz" \
    && curl -fsSL "https://github.com/jetify-com/devbox/releases/download/${DEVBOX_VERSION}/${FILENAME}" -o "/tmp/${FILENAME}" \
    && curl -fsSL "https://github.com/jetify-com/devbox/releases/download/${DEVBOX_VERSION}/checksums.txt" \
        | grep "$FILENAME" | (cd /tmp && sha256sum -c) \
    && tar -xzf "/tmp/${FILENAME}" -C ~/.local/bin devbox \
    && rm "/tmp/${FILENAME}"

# install renovate
ARG RENOVATE_VERSION
USER root
RUN npm install -g "renovate@${RENOVATE_VERSION}"

# install docker
ARG DOCKER_VERSION
RUN ARCH=$([ "$TARGETARCH" = "amd64" ] && echo "x86_64" || echo "aarch64") \
    && FILENAME="docker-${DOCKER_VERSION}.tgz" \
    && curl -fsSL "https://download.docker.com/linux/static/stable/${ARCH}/${FILENAME}" -o "/tmp/${FILENAME}" \
    && tar -xzf "/tmp/${FILENAME}" --strip-components=1 -C /usr/local/bin \
    && rm "/tmp/${FILENAME}" \
    && groupadd --force docker \
    && usermod -aG docker agent
USER agent

# test stage — assertions only, not shipped
FROM base AS test
COPY ["spec.yaml", "test.py", "./"]
COPY --from=root --chown=agent:agent AGENTS.md /home/agent/.claude/AGENTS.md
RUN pip install pyyaml --break-system-packages && python3 test.py

# final image
FROM base
COPY --from=root --chown=agent:agent AGENTS.md /home/agent/.claude/AGENTS.md
