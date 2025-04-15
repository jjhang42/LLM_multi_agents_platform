import os

DOCKERFILES = {
    "orchestrator": "orchestrator/main.py",
    "broker": "broker/main.py",
    "agent_core": "agent_core/main.py",
    "agent_model": "agent_model/main.py",
    "frontend": "frontend"  # 프론트는 main.py 아님
}

PYTHON_TEMPLATE = """FROM python:3.11-slim

WORKDIR /app
COPY ../../requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ../../apps/{name}/ ./{name}/
CMD ["python", "{name}/main.py"]
"""

FRONTEND_TEMPLATE = """# Frontend Dockerfile for Next.js
FROM node:20-alpine AS builder

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
            content = PYTHON_TEMPLATE.format(name=name)
        with open(dockerfile_path, "w") as f:
            f.write(content)
        print(f"[+] Created {dockerfile_path}")

def clean_all():
    for name in DOCKERFILES.keys():
        dockerfile_path = os.path.join(DOCKER_DIR, f"Dockerfile.{name}")
        if os.path.exists(dockerfile_path):
            os.remove(dockerfile_path)
            print(f"[-] Removed {dockerfile_path}")
        else:
            print(f"[!] Not found: {dockerfile_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2 or sys.argv[1] not in ["create", "clean"]:
        print("Usage: python scripts/generate_dockerfile.py [create|clean]")
        exit(1)

    if sys.argv[1] == "create":
        generate_all()
    elif sys.argv[1] == "clean":
        clean_all()
