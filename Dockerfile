# https://docs.docker.com/ai/sandboxes/customize/templates/#build-a-custom-template
FROM docker/sandbox-templates:claude-code AS base
USER agent
ENV PATH="/home/agent/.local/bin:${PATH}"

# install rtk
RUN curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/tags/v0.42.3/install.sh -o /tmp/rtk-install.sh \
    && echo "ab22d109f920db7d931ef6aa97d9460d93f41d296981db8446afed96ea9661e5  /tmp/rtk-install.sh" | sha256sum -c \
    && RTK_VERSION=v0.42.3 sh /tmp/rtk-install.sh \
    && rm /tmp/rtk-install.sh \
    && rtk init -g --auto-patch

    # install caveman
RUN git clone --depth 1 --branch v1.8.2 https://github.com/JuliusBrussee/caveman /tmp/caveman \
    && echo "8ddef49c15f089c26affed3c31d97142c683e1d37a1499ae557281ca09c2712c  /tmp/caveman/install.sh" | sha256sum -c \
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
