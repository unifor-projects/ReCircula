FROM python:3.11-slim

# Install uv from the official image (pinned version for reproducible builds)
COPY --from=ghcr.io/astral-sh/uv:0.4.28 /uv /uvx /bin/

WORKDIR /app

# Install dependencies (cached layer)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy application source
COPY . .

# Make entrypoint executable
RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
