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

# test stage — assertions only, not shipped
FROM base AS test
COPY ["spec.yaml", "test.py", "./"]
RUN pip install pyyaml --break-system-packages && python3 test.py

# final image
FROM base
