import os
import yaml
from jinja2 import Environment, FileSystemLoader

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
OUTPUT_DIR = os.path.join(BASE_DIR, "generated")

env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

def load_config():
    with open(os.path.join(BASE_DIR, "config", "versions.yaml")) as f:
        return yaml.safe_load(f)

def ensure_output():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate():
    cfg = load_config()
    ensure_output()

    cpu_template = env.get_template("Dockerfile.cpu.j2")
    gpu_template = env.get_template("Dockerfile.gpu.j2")

    for py in cfg["python_versions"]:
        ctx = {
            "python_version": py,
            "cuda_version": cfg["cuda"]["version"],
            "cudnn": cfg["cuda"]["cudnn"],
            "ubuntu": cfg["cuda"]["ubuntu"],
            "pytorch_cpu_index": cfg["pytorch"]["cpu_index"],
            "pytorch_gpu_index": cfg["pytorch"]["gpu_index"],
        }

        # CPU
        cpu_out = os.path.join(OUTPUT_DIR, f"Dockerfile.cpu.{py}")
        with open(cpu_out, "w") as f:
            f.write(cpu_template.render(**ctx))

        # GPU
        gpu_out = os.path.join(OUTPUT_DIR, f"Dockerfile.gpu.{py}")
        with open(gpu_out, "w") as f:
            f.write(gpu_template.render(**ctx))

        print(f"Generated for Python {py}")

if __name__ == "__main__":
    generate()