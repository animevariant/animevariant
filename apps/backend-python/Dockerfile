# Base image for both environments
FROM python:3.13-slim AS base

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
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

WORKDIR /workspace 

COPY ./requirements.txt ./
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt
COPY . .
# Set environment variables
ENV MANGANELO="https://ww8.manganelo.tv"
ENV CHAPMANGANELO="https://chapmanganelo.com"
ENV MANGACLASH="https://mangaclash.com"
ENV MANGAPARK="https://mangapark.net"

ENV MANGANELO_CDN="https://cm.blazefast.co"

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
