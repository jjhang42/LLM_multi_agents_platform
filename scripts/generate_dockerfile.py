import os

DOCKERFILES = {
    "orchestrator": "apps/orchestrator/main.py",
    "broker": "apps/broker/main.py",
    "agent_core": "apps/agent_core/main.py",
    "agent_model": "apps/agent_model/main.py",
    "frontend": "frontend"
}

PYTHON_TEMPLATE = """FROM python:3.11-slim

WORKDIR /app

# Use uv (fast Python package installer)
RUN pip install uv

COPY ../../requirements.txt ./
RUN uv pip install --system -r requirements.txt

# Copy the whole project root relative to Docker build context
COPY ../../ ./ 

ENV PYTHONPATH=/app
CMD ["python", "{entrypoint}"]
"""

FRONTEND_TEMPLATE = """# Stage 1: Build
FROM node:20-alpine AS builder

WORKDIR /app

# 설치에 필요한 파일만 먼저 복사 (캐시 최적화)
COPY frontend/package*.json ./
COPY frontend/tsconfig.json ./
COPY frontend/postcss.config.mjs ./
COPY frontend/tailwind.config.js ./
COPY frontend/next.config.mjs ./
RUN npm install

# 나머지 파일 복사
COPY frontend/ ./

# 프로덕션 빌드
RUN npm run build

# Stage 2: Run
FROM node:20-alpine

WORKDIR /app

# 빌드된 결과물 및 설정파일 복사
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/next.config.mjs ./
COPY --from=builder /app/postcss.config.mjs ./
COPY --from=builder /app/tailwind.config.js ./
COPY --from=builder /app/node_modules ./node_modules

EXPOSE 3000

# Next.js 실행 (npx로 바로 next start)
CMD ["npx", "next", "start"]

"""

DOCKER_DIR = "docker"

def generate_all():
    os.makedirs(DOCKER_DIR, exist_ok=True)
    for name, entrypoint in DOCKERFILES.items():
        dockerfile_path = os.path.join(DOCKER_DIR, f"Dockerfile.{name}")
        if name == "frontend":
            content = FRONTEND_TEMPLATE.format(name=name)
        else:
            content = PYTHON_TEMPLATE.format(name=name, entrypoint=entrypoint)
        with open(dockerfile_path, "w") as f:
            f.write(content)
        print(f"Generated {dockerfile_path}")
    print(f"All Dockerfiles saved to ./{DOCKER_DIR}/")

def clean_all():
    for name in DOCKERFILES.keys():
        dockerfile_path = os.path.join(DOCKER_DIR, f"Dockerfile.{name}")
        if os.path.exists(dockerfile_path):
            os.remove(dockerfile_path)
            print(f"Removed {dockerfile_path}")
        else:
            print(f"File not found: {dockerfile_path}")
    print(f"All Dockerfiles cleaned from ./{DOCKER_DIR}/")

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
