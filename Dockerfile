# Production image for the service. Used by the Week 0 exercise and by the Hugging Face Space.
FROM python:3.12-slim

# Links the published package to this repository, so whoever finds the image finds the source.
LABEL org.opencontainers.image.source="https://github.com/anilmodest/ai-eng-track"
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Spaces run containers as uid 1000; so does this image everywhere, so behaviour matches.
RUN useradd -m -u 1000 app
WORKDIR /srv
COPY --chown=app pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY --chown=app app ./app
RUN mkdir -p /srv/data && chown -R app /srv
USER app

ENV PATH="/srv/.venv/bin:$PATH" DATABASE_URL="sqlite:////srv/data/app.db"
EXPOSE 7860
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
