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

FRONTEND_TEMPLATE = """FROM node:20-alpine AS builder

WORKDIR /app
COPY ../../{name}/ ./
RUN npm install
RUN npm run build

FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./
RUN npm install --production

EXPOSE 3000
CMD ["npm", "start"]
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
