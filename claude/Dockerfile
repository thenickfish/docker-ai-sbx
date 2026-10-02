# https://docs.docker.com/ai/sandboxes/customize/templates/#build-a-custom-template
FROM docker/sandbox-templates:claude-code@sha256:bed9d58c654675d3e5c0130c8450d84095b0e227e94a7cda4660d2e4e46033e8 AS base
USER agent
ENV PATH="/home/agent/.local/bin:${PATH}"

ARG RTK_VERSION
ARG RTK_COMMIT
ARG CAVEMAN_VERSION
ARG CAVEMAN_COMMIT
ARG STATUSLINE_VERSION
ARG STATUSLINE_COMMIT

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

# install statusline
RUN git clone --depth 1 --branch "${STATUSLINE_VERSION}" https://github.com/daniel3303/ClaudeCodeStatusLine /tmp/statusline \
    && test "$(git -C /tmp/statusline rev-parse HEAD)" = "${STATUSLINE_COMMIT}" \
    && mkdir -p ~/.claude/statusline \
    && cp /tmp/statusline/statusline.sh ~/.claude/statusline/statusline.sh \
    && chmod +x ~/.claude/statusline/statusline.sh \
    && rm -rf /tmp/statusline

# install devbox
ARG DEVBOX_VERSION
ARG TARGETARCH
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

# test stage — assertions only, not shipped
FROM base AS test
COPY ["spec.yaml", "test.py", "./"]
COPY files/ ./files/
RUN pip install pyyaml --break-system-packages && python3 test.py

# final image
FROM base
