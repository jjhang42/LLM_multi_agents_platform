import os

DOCKERFILES = {
    "orchestrator": "apps/orchestrator/main.py",
    "broker": "apps/broker/main.py",
    "agent_core": "apps/agent_core/main.py",
    "agent_creator": "apps/agent_creator/main.py",
    "agent_researcher": "apps/agent_researcher/main.py",   # ✅ 추가
    "agent_publisher": "apps/agent_publisher/main.py",     # ✅ 추가
    "api_gateway": "apps/api_gateway/main.py",
    "frontend": "frontend"
}

PYTHON_TEMPLATE = """FROM python:3.11-slim

WORKDIR /app

# 공통 필수 패키지
RUN pip install --no-cache-dir uvicorn httpx fastapi python-dotenv

{extra_install}

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

COPY --from=builder /app /app

EXPOSE 3000
CMD ["npm", "run", "start"]
"""

DOCKER_DIR = "docker"

def generate_all():
    os.makedirs(DOCKER_DIR, exist_ok=True)

    for name, entrypoint in DOCKERFILES.items():
        dockerfile_path = os.path.join(DOCKER_DIR, f"Dockerfile.{name}")

        if name == "frontend":
            content = FRONTEND_TEMPLATE
        else:
            # 실행 명령어 설정
            if name in ["api_gateway", "orchestrator", "broker"]:
                module_path = entrypoint[:-3].replace('/', '.')
                cmd = f'CMD ["uvicorn", "{module_path}:app", "--host", "0.0.0.0", "--port", "8000"]'
            else:
                cmd = f'CMD ["python", "{entrypoint}"]'

            # 서비스별 의존성 설정
            extra_install = ""
            if name.startswith("agent_"):
                extra_install = (
                    "RUN pip uninstall -y google || true && "
                    "pip install --no-cache-dir protobuf==4.25.3 && "
                    "pip install --no-cache-dir google-generativeai==0.2.0 Pillow && "
                    "pip install --no-cache-dir crewai"
                )
            elif name == "broker":
                extra_install = (
                    "RUN pip install --no-cache-dir pyyaml pydantic-settings"
                )

            content = PYTHON_TEMPLATE.replace("{cmd}", cmd).replace("{extra_install}", extra_install)

        with open(dockerfile_path, "w") as f:
            f.write(content)

        print(f"✅ Generated {dockerfile_path}")

    print("📁 All Dockerfiles saved to ./docker/")

def clean_all():
    for name in DOCKERFILES.keys():
        dockerfile_path = os.path.join(DOCKER_DIR, f"Dockerfile.{name}")
        if os.path.exists(dockerfile_path):
            os.remove(dockerfile_path)
            print(f"🗑️ Removed {dockerfile_path}")
        else:
            print(f"⚠️ File not found: {dockerfile_path}")
    print(f"🧹 All Dockerfiles cleaned from ./docker/")

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
