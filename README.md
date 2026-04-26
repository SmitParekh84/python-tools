---
title: Smit Parekh — Python Tools
emoji: ✂️
colorFrom: blue
colorTo: cyan
sdk: docker
app_port: 7860
pinned: false
---

# python-tools

FastAPI service powering the ML-backed tools on
[smitparekh.co.in](https://smitparekh.co.in) — currently background removal,
with room for upscaling, OCR, transcription, etc.

The frontmatter above is what **Hugging Face Spaces** reads when you push this
folder as a Docker Space.

## Endpoints

| Method | Path             | Notes                                 |
|--------|------------------|---------------------------------------|
| GET    | `/api/health`    | Liveness probe + active model name    |
| POST   | `/api/remove-bg` | multipart/form-data `file` → PNG blob |
| GET    | `/docs`          | Swagger UI                            |

`POST /api/remove-bg` accepts `image/png`, `image/jpeg`, `image/webp`
(default 10 MB cap) and returns a transparent `image/png`.

## Local development

```bash
cd python-tools
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 7860
```

Visit http://localhost:7860/docs.

## Configuration

Copy `.env.example` to `.env` and adjust as needed.

| Variable          | Default                                        | Purpose                         |
|-------------------|------------------------------------------------|---------------------------------|
| `ALLOWED_ORIGINS` | `http://localhost:3000,http://localhost:3001`  | CORS allowlist (comma list or `*`) |
| `REMBG_MODEL`     | `u2net`                                        | rembg model: `u2net`, `u2netp`, `u2net_human_seg`, `isnet-general-use`, `birefnet-general` |
| `MAX_UPLOAD_MB`   | `10`                                           | Per-request upload cap          |

## Deploy to Hugging Face Spaces (Docker)

1. Create a new Space → SDK **Docker**, hardware **CPU basic** (free, 16 GB RAM).
2. From this folder:

   ```bash
   git init
   git remote add hf https://huggingface.co/spaces/<your-user>/python-tools
   git add .
   git commit -m "feat: initial python tools service"
   git push hf main
   ```
3. Wait for the build (~5–8 min — model is baked into the image).
4. Set `ALLOWED_ORIGINS` in **Settings → Variables and secrets**, e.g.
   `https://smitparekh.co.in,https://smitparekh-web.vercel.app`.
5. Point the frontend at it: in `new-frontend/.env.local`,

   ```
   NEXT_PUBLIC_PYTHON_API_URL=https://<your-user>-python-tools.hf.space
   ```

## Docker (anywhere else)

```bash
docker build -t portfolio-python-tools .
docker run --rm -p 7860:7860 \
  -e ALLOWED_ORIGINS="http://localhost:3000" \
  portfolio-python-tools
```

## Adding more tools

1. Drop a router file in `app/routers/<name>.py` exposing an `APIRouter`.
2. Wire it up in `app/main.py` with `app.include_router(...)`.
3. Add the corresponding typed call in
   `new-frontend/lib/api/<name>.ts` and a hook in
   `new-frontend/hooks/api/use-<name>.ts`.

## Notes

- **Cold starts on HF Spaces:** ~30–60 s after 48 h idle. The model is
  pre-downloaded into the Docker image (see `Dockerfile`) so requests
  served by a *warm* container are fast.
- **u2net** model lives at `/tmp/.u2net` inside the container (writable).
- Logs go to stdout; HF Spaces captures them.
