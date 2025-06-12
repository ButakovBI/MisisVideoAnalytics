import json
import subprocess
import argparse
import sys
from pathlib import Path


def build_image(repo_root: Path, svc: str, conf: dict) -> str:
    dockerfile_path = repo_root / conf['dockerfile']
    image = f"misis-{svc}"
    cmd = ['docker', 'build', '-f', str(dockerfile_path), '-t', image]
    if 'LIBS' in conf:
        cmd += ['--build-arg', f"LIBS={' '.join(conf['LIBS'])}"]
    cmd.append(str(repo_root))
    print(f"Building image {image} (Dockerfile: {conf['dockerfile']})…")
    subprocess.check_call(cmd)
    return image


def run_container(image: str, cmd_override: list[str] | None = None):
    cmd = ['docker', 'run', '--rm', image]
    if cmd_override:
        cmd += cmd_override
        print(f"Running {image} with override: {' '.join(cmd_override)}…")
    else:
        print(f"Running {image}…")
    subprocess.check_call(cmd)


def run_compose(compose_file: Path):
    print(f"Bringing up stack '{compose_file.name}'…")
    subprocess.check_call([
        'docker-compose', '-f', str(compose_file),
        'up', '--abort-on-container-exit'
    ])
    print(f"Tearing down stack '{compose_file.name}'…")
    subprocess.call([
        'docker-compose', '-f', str(compose_file),
        'down', '--volumes'
    ])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config',
                        default='build/docker/images_configuration.json',
                        help='Path to JSON config')
    parser.add_argument('--test', action='store_true',
                        help='Build test images and run all tests')
    args = parser.parse_args()

    try:
        cfg = json.load(open(args.config))
    except Exception as e:
        print(f"Failed to load config: {e}", file=sys.stderr)
        sys.exit(1)

    repo_root = Path(__file__).resolve().parents[2]

    if args.test:
        test_services = [svc for svc in cfg if svc.startswith('test_')]
        for svc in test_services:
            build_image(repo_root, svc, cfg[svc])

        for svc in test_services:
            conf = cfg[svc]
            image = f"misis-{svc}"

            if 'compose_file' in conf:
                compose_file = repo_root / conf['compose_file']
                run_compose(compose_file)
            else:
                cmd_override = conf.get('cmd_override')
                run_container(image, cmd_override)

    else:
        for svc, conf in cfg.items():
            if not svc.startswith('test_'):
                build_image(repo_root, svc, conf)

        print("Deploying production services…")
        prod_compose = repo_root / 'build' / 'docker' / 'docker_compose.yml'
        subprocess.check_call(['docker-compose', '-f', str(prod_compose), 'up', '-d'])


if __name__ == '__main__':
    main()
