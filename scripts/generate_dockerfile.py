import os

DOCKERFILES = {
    "orchestrator": "apps/orchestrator/main.py",
    "broker": "apps/broker/main.py",
    "agent_core": "apps/agent_core/main.py",
    "agent_model": "apps/agent_model/main.py",
    "api_gateway": "apps/api_gateway/main.py",
    "frontend": "frontend"
}

PYTHON_TEMPLATE = """FROM python:3.11-slim

WORKDIR /app

RUN pip install uvicorn httpx fastapi uv
COPY ../../requirements.txt ./
RUN uv pip install --system -r requirements.txt

COPY ../../ ./

ENV PYTHONPATH=/app
{cmd}
"""

FRONTEND_TEMPLATE = """# Stage 1: Build
FROM node:20-alpine AS builder
WORKDIR /app

COPY frontend/package*.json ./
COPY frontend/tsconfig.json ./
COPY frontend/postcss.config.js ./
COPY frontend/tailwind.config.js ./
COPY frontend/next.config.js ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# Stage 2: Run
FROM node:20-alpine
WORKDIR /app

ENV NODE_ENV=production

# ✅ 이 부분: server.js가 포함된 standalone 디렉토리를 전체 복사
COPY --from=builder /app/.next/standalone /app

# ✅ 정적 파일 및 public 디렉토리도 같이 복사
COPY --from=builder /app/.next/static .next/static
COPY --from=builder /app/public public

EXPOSE 3000
# ✅ server.js는 이제 /app/server.js에 있으므로 다음과 같이 실행
CMD ["node", "server.js"]
"""


DOCKER_DIR = "docker"

def generate_all():
    os.makedirs(DOCKER_DIR, exist_ok=True)
    for name, entrypoint in DOCKERFILES.items():
        dockerfile_path = os.path.join(DOCKER_DIR, f"Dockerfile.{name}")

        if name == "frontend":
            content = FRONTEND_TEMPLATE
        else:
            if name in ["api_gateway", "orchestrator", "broker"]:
                module_path = entrypoint[:-3].replace('/', '.')
                cmd = f'CMD ["uvicorn", "{module_path}:app", "--host", "0.0.0.0", "--port", "8000"]'
            else:
                cmd = f'CMD ["python", "{entrypoint}"]'
            content = PYTHON_TEMPLATE.replace("{entrypoint}", entrypoint).replace("{cmd}", cmd)

        with open(dockerfile_path, "w") as f:
            f.write(content)
        print(f"✅ Generated {dockerfile_path}")
    print(f"📁 All Dockerfiles saved to ./{DOCKER_DIR}/")

def clean_all():
    for name in DOCKERFILES.keys():
        dockerfile_path = os.path.join(DOCKER_DIR, f"Dockerfile.{name}")
        if os.path.exists(dockerfile_path):
            os.remove(dockerfile_path)
            print(f"🗑️ Removed {dockerfile_path}")
        else:
            print(f"⚠️ File not found: {dockerfile_path}")
    print(f"🧹 All Dockerfiles cleaned from ./{DOCKER_DIR}/")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2 or sys.argv[1] not in ["create", "clean"]:
        print("Usage:")
        print("  python scripts/generate_dockerfile.py create   # generate all Dockerfiles")
        print("  python scripts/generate_dockerfile.py clean    # delete generated Dockerfiles")
        exit(1)

    if sys.argv[1] == "create":
        generate_all()
    elif sys.argv[1] == "clean":
        clean_all()
