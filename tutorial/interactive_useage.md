# 🐳 Interactive Python Development with Docker

This guide explains how to use Docker as a **fully interactive development environment** for a Python project using the base image:

```
ghcr.io/halmosb/docker-builder/python:3.14-cpu
```

The goal is to:

* Work on your code locally
* Execute it inside a container
* Install missing dependencies dynamically
* Keep your host system clean

---

## 📦 1. Project Structure

A typical project layout:

```
my-project/
├── src/
├── tests/
├── requirements.txt
├── pyproject.toml   # optional
├── Dockerfile       # optional (for extending image)
└── README.md
```

---

## 🚀 2. Start an Interactive Development Container

Run the container with your project mounted:

```
docker run -it --rm \
  -v $(pwd):/workspace \
  -w /workspace \
  ghcr.io/halmosb/docker-builder/python:3.14-cpu \
  bash
```

### Explanation

* `-it`: interactive terminal
* `--rm`: clean up container after exit
* `-v $(pwd):/workspace`: mount your project
* `-w /workspace`: set working directory

Now you are **inside the container**, but editing files on your host.

---

## 🧪 3. Install Additional Dependencies

Your base image does not include all libraries. Install what you need:

```
pip install -r requirements.txt
```

Or manually:

```
pip install numpy pandas matplotlib
```

💡 These installs are **ephemeral** unless persisted (see below).

---

## 💾 4. Persist Installed Packages (Recommended)

### Option A: Use a Docker Volume for pip cache

```
cd my-project

docker run -it --rm \
  -v $(pwd):/workspace \
  -v pip-cache:/root/.cache/pip \
  -w /workspace \
  ghcr.io/halmosb/docker-builder/python:3.14-cpu \
  bash
```

---

### Option B: Extend the Base Image (Better for stability)

Create a `Dockerfile`:

```
FROM ghcr.io/halmosb/docker-builder/python:3.14-cpu

WORKDIR /workspace

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```

Build:

```
docker build -t my-python-dev .
```

Run:

```
docker run -it --rm \
  -v $(pwd):/workspace \
  -w /workspace \
  my-python-dev \
  bash
```

---

## 🛠️ 5. Developer Workflow

Inside the container:

### Run your code

```
python src/main.py
```

### Run tests

```
pytest
```

### Format / lint

```
black .
flake8 .
```

---

## 🔄 6. Live Editing Workflow

* Edit code on your host (VSCode, Vim, etc.)
* Code is instantly visible inside the container
* Re-run scripts/tests without rebuilding

---

## 🧠 7. Optional: Use VS Code Dev Containers

If you use VS Code:

1. Install **Dev Containers extension**
2. Add `.devcontainer/devcontainer.json`:

```
{
  "image": "ghcr.io/halmosb/docker-builder/python:3.14-cpu",
  "workspaceFolder": "/workspace",
  "mounts": [
    "source=${localWorkspaceFolder},target=/workspace,type=bind"
  ]
}
```

3. Open project → *Reopen in Container*

---

## 📊 8. GPU / CPU Variants

You are using a CPU image:

```
python:3.14-cpu
```

If GPU is needed later, switch to a CUDA-enabled image and add:

```
--gpus all
```

---

## 🧹 9. Cleanup

List containers:

```
docker ps -a
```

Remove unused volumes:

```
docker volume prune
```

---

## ⚡ Summary

| Task                | Command                   |
| ------------------- | ------------------------- |
| Start dev container | `docker run -it ... bash` |
| Install deps        | `pip install ...`         |
| Persist deps        | Dockerfile                |
| Run code            | `python ...`              |
| Run tests           | `pytest`                  |

---

## 🧩 Key Idea

Docker is not just for deployment — here it acts as a:

> **Reproducible, isolated, portable development environment**

You get:

* No system pollution
* Exact dependency control
* Easy sharing across machines

---

## 🔚

This workflow is minimal, flexible, and scales from quick experiments to production-grade environments.
