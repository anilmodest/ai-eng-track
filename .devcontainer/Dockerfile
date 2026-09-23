# The devcontainer base. Built before any feature installs, which is the point: the stock image
# ships an apt source for yarn whose signing key has expired, so the first `apt-get update` in a
# later layer (a feature, for instance) fails with exit 100 and the whole Codespace drops into a
# recovery container. We do not use yarn; remove the source once, here.
#
# Pinned to bookworm on purpose: the rolling python:3.12 tag now resolves to Debian trixie, where
# docker-in-docker's moby packages do not exist. Re-check both when the images settle.
FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

RUN rm -f /etc/apt/sources.list.d/yarn.list \
 && apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates curl \
 && rm -rf /var/lib/apt/lists/*

# uv in the image, not in a home directory: every shell finds it, interactive or not, and the
# post-create step is then just a sync. (Installing it per-container put it in ~/.local/bin,
# which a non-interactive shell does not have on PATH.)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/
ENV UV_LINK_MODE=copy
