# Stage 1: Build environment
FROM alpine:3.19 AS builder

# Install only absolutely necessary build dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    freetype-dev \
    libpng-dev \
    geos-dev \
    g++ \
    python3-dev \
    musl-dev \
    ttf-dejavu \
    fontconfig

# Create virtual environment and optimize pip installations
RUN python3 -m venv /venv && \
    /venv/bin/pip install --no-cache-dir --compile \
    wheel && \
    /venv/bin/pip install --no-cache-dir --compile \
    cython==3.0.10 \
    numpy==1.26.0 && \
    /venv/bin/pip install --no-cache-dir --compile \
    pandas==2.1.3 \
    matplotlib==3.8.0 \
    shapely==2.0.3 \
    colour-science==0.4.2 \
    scipy==1.11.4

# Aggressive cleanup
RUN find /venv -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true && \
    find /venv -type d -name "doc" -exec rm -rf {} + 2>/dev/null || true && \
    find /venv -name "*.pyc" -delete && \
    find /venv -name "__pycache__" -exec rm -rf {} + && \
    find /venv -name "*.so" -exec strip --strip-unneeded {} \; && \
    rm -rf /venv/lib/python3.11/site-packages/scipy/io* \
           /venv/lib/python3.11/site-packages/matplotlib/mpl-data/sample_data \
           /venv/lib/python3.11/site-packages/matplotlib/mpl-data/fonts/afm \
           /venv/lib/python3.11/site-packages/matplotlib/mpl-data/fonts/pdfcorefonts \
           /venv/lib/python3.11/site-packages/shapely/tests \
           /venv/lib/python3.11/site-packages/numpy/tests \
           /venv/lib/python3.11/site-packages/pandas/tests \
           /venv/share/* \
           /venv/lib/python3.11/site-packages/pip* \
           /venv/lib/python3.11/site-packages/setuptools* \
           /venv/lib/python3.11/site-packages/wheel*

# Stage 2: Runtime (minimal)
FROM alpine:3.19

# Install only required runtime packages
RUN apk add --no-cache \
    libstdc++ \
    python3 \
    ttf-dejavu \
    geos \
    freetype \
    libpng

# Copy only necessary files from builder
COPY --from=builder /venv /venv

# Copy application files with explicit verification
COPY scripts/*.py /usr/local/bin/
COPY entrypoint.sh /usr/local/bin/

# Make all scripts executable
RUN chmod +x /usr/local/bin/*.py /usr/local/bin/entrypoint.sh

# Configure environment with minimal settings
ENV PATH="/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/venv/lib/python3.11/site-packages" \
    MPLCONFIGDIR="/tmp/matplotlib"

# Create minimal matplotlib config and data directory
RUN mkdir -p /tmp/matplotlib /data && \
    echo "backend: Agg" > /tmp/matplotlib/matplotlibrc

VOLUME ["/data"]
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
