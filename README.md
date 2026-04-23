# 🐳 Python Docker Image Generator (GHCR + CI)

This repository provides a **config-driven system to generate, build, and publish Python Docker images** automatically using **GitHub Actions** and **GitHub Container Registry (GHCR)**.

It is designed to:

* Generate Dockerfiles for multiple Python versions
* Build CPU-only images reproducibly
* Push versioned and rolling tags to GHCR
* Use caching to accelerate CI builds

---

## 📦 Features

* ✅ Configurable Python versions via YAML
* ✅ Automatic Dockerfile generation
* ✅ GitHub Actions CI/CD pipeline
* ✅ Tagged image publishing (`vX.Y.Z`)
* ✅ Automatic `latest` tagging (configurable)
* ✅ Layer caching via registry
* ✅ Clean naming conventions for images

---

## 📁 Repository Structure

```text
.
├── .github/workflows/
│   └── docker-build.yml     # CI pipeline
├── config/
│   └── versions.yaml        # Defines Python versions
├── generated/               # Auto-generated Dockerfiles
├── scripts/
│   ├── build.sh              # Building container locally   
│   ├── clean.sh              # Cleaning local containers   
│   ├── generate.py           # Generates the Dockerfiles  
│   └── run.sh                # Runs a docker container locally
├── templates/               # Template Dockerfiles
│   ├── Dockerfile.cpu.j2     # CPU Dockerfile template  
│   └── Dockerfile.gpu.j2     # GPU Dockerfile template
├── .gitignore               # Not tracked files
├── LICENSE                  # License file
├── README.md                # Usage info
└── requirements.txt         # Requirements
```

---

## ⚙️ Configuration

### Python Versions

Edit:

```yaml
# config/versions.yaml
python_versions:
  - "3.10"
  - "3.11"
  - "3.12"
  - "3.13"
  - "3.14"
```

These versions will:

* Drive Dockerfile generation
* Define CI build matrix
* Control published image tags

---

## 🏗️ Dockerfile Generation

Run locally:

```bash
pip install -r requirements.txt
python scripts/generate.py
```

This will create:

```text
generated/
├── Dockerfile.cpu.3.13
├── Dockerfile.cpu.3.14
...
```

---

## 🚀 CI/CD Pipeline

### Trigger

The workflow runs when you push a tag:

```bash
git commit -m "Commit message"
git tag v1.0.0
git push origin v1.0.0
```

### What happens

1. Extracts the Git tag (`v1.0.0`)
2. Reads Python versions from config
3. Generates Dockerfiles
4. Builds images (CPU only)
5. Pushes to GHCR
6. Applies tags

---

## 🐳 Published Images

Images are published to:

```text
ghcr.io/bhalmos/docker-builder/python
```

### Tag format

For each Python version for CPU:

```text
ghcr.io/bhalmos/docker-builder/python:<python-version>-cpu-<git-tag>
ghcr.io/bhalmos/docker-builder/python:<python-version>-cpu
```
and for GPU:
```text
ghcr.io/bhalmos/docker-builder/python:<python-version>-gpu-<git-tag>
ghcr.io/bhalmos/docker-builder/python:<python-version>-gpu
```

Example:

```text
ghcr.io/bhalmos/docker-builder/python:3.14-cpu-v0.0.2
ghcr.io/bhalmos/docker-builder/python:3.14-gpu
```

### Latest tag

Optionally:

```text
ghcr.io/bhalmos/docker-builder/python:latest
```

Typically mapped to a chosen version (e.g. 3.14-cpu).

---

## 📥 Using the Images

### Pull

```bash
docker pull ghcr.io/bhalmos/docker-builder/python:3.14-cpu
```

### Use in Dockerfile

```Dockerfile
FROM ghcr.io/bhalmos/docker-builder/python:3.14-cpu
```

### Use in GitHub Actions

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    container:
      image: ghcr.io/bhalmos/docker-builder/python:3.14-cpu
```

---

## ⚡ Caching Strategy

The workflow uses registry-based caching:

```yaml
cache-from: type=registry,ref=ghcr.io/bhalmos/docker-builder/cache
cache-to: type=registry,ref=ghcr.io/bhalmos/docker-builder/cache,mode=max
```

### Benefits

* Faster rebuilds
* Reduced CI time
* Persistent cache across runs

---

## 🔐 Authentication

Publishing uses the built-in GitHub token:

```yaml
username: ${{ github.actor }}
password: ${{ secrets.GITHUB_TOKEN }}
```

### Requirements

* `packages: write` permission must be enabled in workflow
* Repository must allow GHCR publishing

---

## 🧪 Local Build (Optional)

You can build images locally:

```bash
docker build \
  -f generated/Dockerfile.cpu.3.14 \
  -t test-python:3.14 .
```

---

## 🛠️ Customization

### Add dependencies to images

Modify `scripts/generate.py` to:

* Install system packages
* Add Python dependencies
* Configure environment

---

## ⚠️ Known Limitations

* No multi-architecture images (yet)
* No automatic cleanup of old tags

---

## 🧩 Future Improvements

* Automatic pruning of old images
* Semantic version branching (e.g. `3.14-latest`)
* Parallel matrix optimizations

---

## 📄 License

GNUv3.

---

## 🤝 Contributing

Contributions are welcome. Typical improvements include:

* New base image strategies
* Performance optimizations
* Additional configuration options
