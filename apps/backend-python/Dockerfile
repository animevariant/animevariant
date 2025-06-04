# Stage 1: Install dependencies
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS deps
WORKDIR /workspace
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency definitions first (for better caching)
COPY pyproject.toml uv.lock* ./

# Install only the dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Stage 2: Base image for both environments
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS base
WORKDIR /workspace
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

RUN apt-get update && apt-get install -y \
    python3-dev \
    build-essential \
    portaudio19-dev \
    libsdl2-dev \
    alsa-utils \
    pulseaudio \
    git \
    curl \
    wget \
    unzip \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Copy the dependencies from the previous stage
COPY --from=deps /workspace/.venv/ /workspace/.venv/

# Copy application code
COPY . .

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install the project (dependencies are already installed)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Set environment variables
ENV MANGANELO="https://ww8.manganelo.tv"
ENV CHAPMANGANELO="https://chapmanganelo.com"
ENV MANGACLASH="https://mangaclash.com"
ENV MANGAPARK="https://mangapark.net"
ENV MANGANELO_CDN="https://cm.blazefast.co"

# Set the path to include the virtual environment
ENV PATH="/workspace/.venv/bin:$PATH"

# Development-specific stage
FROM base AS dev

# Install Neovim dependencies
RUN curl -LO https://github.com/neovim/neovim/releases/latest/download/nvim-linux64.tar.gz \
    && sudo rm -rf /opt/nvim \
    && sudo tar -C /opt -xzf nvim-linux64.tar.gz \
    && echo 'export PATH="$PATH:/opt/nvim-linux64/bin"' >> ~/.bashrc \
    && chmod +x ~/.bashrc \
    && ~/.bashrc \
    && git clone https://github.com/nvim-lua/kickstart.nvim.git "${XDG_CONFIG_HOME:-$HOME/.config}"/nvim

# Expose ports used in development
EXPOSE 8000 8001 5173 5174 4173

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]

# Production-specific stage
FROM base AS prod

# Expose only the necessary production port
EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
