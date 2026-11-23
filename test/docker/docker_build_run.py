import docker
from pathlib import Path

IP = "0.0.0.0"
PORT = "8000"
img_tag = "test-img"
container_name = "test-container"
client = docker.from_env(timeout=86400)
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def build():
    client.images.build(path=str(PROJECT_ROOT), tag=img_tag)
    print("Container is built.")


def run():
    client.containers.run(
        img_tag, ports={"8000/tcp": 8000}, name=container_name, detach=True
    )
    print("Container is running.")


if __name__ == "__main__":
    build()
    run()
