# Production image for the service (Week 0 exercise: deploy something other people can reach)
FROM python:3.12-slim
WORKDIR /srv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY app ./app
ENV PATH="/srv/.venv/bin:$PATH" DATABASE_URL="sqlite:////srv/data/app.db"
RUN mkdir -p /srv/data
EXPOSE 7860
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
