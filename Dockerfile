# Hugging Face Docker Space — FastAPI + rembg
# Docs: https://huggingface.co/docs/hub/spaces-sdks-docker
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    # rembg model cache — must be writable on HF Spaces
    U2NET_HOME=/tmp/.u2net \
    XDG_CACHE_HOME=/tmp/.cache \
    HOME=/tmp \
    PORT=7860

# System libs needed by Pillow / opencv / onnxruntime
RUN apt-get update && apt-get install -y --no-install-recommends \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender1 \
        libgl1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

# Pre-download the default u2net model into the image so the first
# request doesn't pay the download tax. Comment out if you want a
# smaller image and lazy-load at runtime instead.
RUN python -c "from rembg import new_session; new_session('u2net')"

COPY app ./app

EXPOSE 7860

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
