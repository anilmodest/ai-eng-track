# Production image for the service: week 0, the release workflow, and the programme's hidden
# evaluation, which builds it from your repository and runs it with no internet.
FROM python:3.12-slim

# Links the published package to your repository, so whoever finds the image finds the source.
# The release workflow passes it; nothing here names an owner.
ARG SOURCE=""
LABEL org.opencontainers.image.source=$SOURCE
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# A fixed non-root user, the same on every machine that runs the image, so file ownership in
# /srv/data never depends on where it runs.
RUN useradd -m -u 1000 app
WORKDIR /srv
COPY --chown=app pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY --chown=app app ./app
# The desk's customers and tickets, loaded into the database at start (app/support.py).
COPY --chown=app support ./support
RUN mkdir -p /srv/data && chown -R app /srv
USER app

ENV PATH="/srv/.venv/bin:$PATH" DATABASE_URL="sqlite:////srv/data/app.db"
# The programme's runner and the release workflow both expect the service on 7860.
EXPOSE 7860
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
