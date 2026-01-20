# syntax=docker/dockerfile:1.7
FROM python:3.12-slim

# System deps (add build tools if needed for scientific libs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git build-essential curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install runtime deps first to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY pyproject.toml setup.cfg MANIFEST.in ./
COPY src ./src

# Editable install isn't typical in Docker; install package
RUN pip install --no-cache-dir .

# Expose a default port for API/GUI (adjust as needed)
EXPOSE 8000

# Default command (CLI help); override in docker-compose or run args
CMD ["uqbar", "--help"]

####################################################################

# A small Linux base
FROM ubuntu:24.04

# System deps for micromamba + SSL + basic tooling
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl bzip2 \
 && rm -rf /var/lib/apt/lists/*

# Install micromamba
ENV MAMBA_ROOT_PREFIX=/opt/micromamba
RUN curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest \
  | tar -xvj -C /usr/local/bin --strip-components=1 bin/micromamba

# Copy env specs first (better Docker layer caching)
WORKDIR /app
COPY environment.yml /app/environment.yml
COPY requirements-pip.txt /app/requirements-pip.txt

# Create the conda env
RUN micromamba create -y -n web -f /app/environment.yml \
 && micromamba clean -a -y

# Install pip fallback packages INTO the same env
RUN micromamba run -n web python -m pip install --no-cache-dir -r /app/requirements-pip.txt

# Copy your code last (so code edits don't rebuild the env)
COPY app.py /app/app.py

# Default command
CMD ["micromamba", "run", "-n", "web", "python", "app.py"]